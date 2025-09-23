import socket
import time
from threading import Thread
from pathlib import Path
from typing import Optional, Dict, Any

class TSCPrinter:
    def __init__(self, printer_ip: str = "192.168.1.200", printer_port: int = 9100):
        self.printer_ip = printer_ip
        self.printer_port = printer_port
        self.socket = None

    def connect_printer(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.printer_ip, self.printer_port))
            return True
        except Exception as e:
            print(f"connect_printer Exception for {self.printer_ip}: {e}")
            return False

    def disconnect_printer(self):
        """Disconnect from printer"""
        try:
            if self.socket:
                self.socket.close()
                self.socket = None
        except Exception as e:
            print(f"disconnect_printer Exception: {e}")

    def check_connection(self, timeout: int = 3) -> bool:
        """Check if printer is online and reachable"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((self.printer_ip, self.printer_port))
            sock.close()
            return result == 0
        except Exception as e:
            print(f"Connection check error for {self.printer_ip}: {e}")
            return False

    def is_connected(self) -> bool:
        """Check if socket is connected"""
        try:
            if self.socket:
                # Try to send a small packet to check connection
                self.socket.send(b'')
                return True
        except:
            self.socket = None
        return False

    def wait_response(self):
        while True:
            try:
                response = self.socket.recv(1024)
                if response:
                    print(f"Yanıt: {response.decode('utf-8', errors='ignore').strip()}")
                else:
                    print("Yanıt Alınmadı.")
            except Exception as e:
                print("wait_response Exception:",e)

            time.sleep(0.1)

    def send_test(self,data):
        try:
            text = f"TEXT 10,10,\"2\",0,1,1,\"{data}\"\n"
            test_commands = [
                b"CLS\n",
                b"SIZE 100 mm, 20 mm\n",
                bytes(text, "utf-8"),
                b"PRINT 1,1\n"
            ]
            
            for cmd in test_commands:
                print(f"📤 Socket komut: {cmd.decode().strip()}")
                self.socket.send(cmd)
                time.sleep(0.5)
        except Exception as e:
            print("send_test Exception:",e)

    def send_bmp(self, bmp_path: str = "logo.bmp", width_mm: int = 100, height_mm: int = 29):
        """
        Send BMP file to printer and print it
        
        Args:
            bmp_path: Path to BMP file
            width_mm: Label width in mm
            height_mm: Label height in mm
        """
        try:
            if not self.is_connected():
                if not self.connect_printer():
                    raise Exception(f"Could not connect to printer {self.printer_ip}")
            
            bmp_file = Path(bmp_path)
            if not bmp_file.exists():
                raise Exception(f"BMP file not found: {bmp_path}")
            
            fname = bmp_file.name.upper()
            bmp_bytes = bmp_file.read_bytes()
            
            # TSPL command to download and print the BMP
            tspl_after_download = f"""
SIZE {width_mm} mm,{height_mm} mm
DIRECTION 1
CLS
PUTBMP 0,0,"{fname}"
PRINT 1
""".lstrip().encode("ascii")
            
            header = f'DOWNLOAD "{fname}",{len(bmp_bytes)},'.encode("ascii")
            
            # Send BMP file to printer
            self.socket.sendall(header + bmp_bytes + b"\n")
            time.sleep(0.5)  # Wait a bit for download
            
            # Send print command
            self.socket.sendall(tspl_after_download)
            print(f"Successfully sent {bmp_path} to printer {self.printer_ip}")
            return True
            
        except Exception as e:
            print(f"send_bmp Exception for {self.printer_ip}: {e}")
            return False

    def send_text(self, text: str, x: int = 10, y: int = 10, width_mm: int = 100, height_mm: int = 29):
        """
        Send text to printer and print it
        
        Args:
            text: Text to print
            x: X coordinate
            y: Y coordinate
            width_mm: Label width in mm
            height_mm: Label height in mm
        """
        try:
            if not self.is_connected():
                if not self.connect_printer():
                    raise Exception(f"Could not connect to printer {self.printer_ip}")
            
            tspl_command = f"""
SIZE {width_mm} mm, {height_mm} mm
DIRECTION 1
CLS
TEXT {x},{y},"2",0,1,1,"{text}"
PRINT 1
""".lstrip().encode("ascii")
            
            self.socket.sendall(tspl_command)
            print(f"Successfully sent text '{text}' to printer {self.printer_ip}")
            return True
            
        except Exception as e:
            print(f"send_text Exception for {self.printer_ip}: {e}")
            return False

class PrinterManager:
    """Manager class for handling multiple printers"""
    
    def __init__(self):
        self.printers = {}  # Cache for printer connections
    
    def get_printer(self, ip: str, port: int = 9100) -> TSCPrinter:
        """Get or create a printer instance"""
        key = f"{ip}:{port}"
        if key not in self.printers:
            self.printers[key] = TSCPrinter(ip, port)
        return self.printers[key]
    
    def check_printer_connection(self, ip: str, port: int = 9100, timeout: int = 3) -> bool:
        """Check if printer is online and reachable"""
        printer = self.get_printer(ip, port)
        return printer.check_connection(timeout)
    
    def get_printer_status(self, ip: str, port: int = 9100) -> Dict[str, Any]:
        """Get printer status including connection info"""
        is_online = self.check_printer_connection(ip, port)
        return {
            "ip": ip,
            "port": port,
            "is_online": is_online,
            "status": "Online" if is_online else "Offline"
        }
    
    def print_bmp(self, ip: str, bmp_path: str, width_mm: int = 100, height_mm: int = 29, port: int = 9100) -> bool:
        """Print BMP file to specified printer"""
        printer = self.get_printer(ip, port)
        return printer.send_bmp(bmp_path, width_mm, height_mm)
    
    def print_text(self, ip: str, text: str, x: int = 10, y: int = 10, width_mm: int = 100, height_mm: int = 29, port: int = 9100) -> bool:
        """Print text to specified printer"""
        printer = self.get_printer(ip, port)
        return printer.send_text(text, x, y, width_mm, height_mm)
    
    def disconnect_all(self):
        """Disconnect all cached printers"""
        for printer in self.printers.values():
            printer.disconnect_printer()
        self.printers.clear()

# Global printer manager instance
printer_manager = PrinterManager()
