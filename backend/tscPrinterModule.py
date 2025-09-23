import socket
import time
from threading import Thread
from pathlib import Path

class TSCPrinter:
    def __init__(self):
        self.printer_ip = "192.168.1.200"
        self.printer_port = 9100
        self.socket = None

    def connect_printer(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.printer_ip,self.printer_port))
        except Exception as e:
            print("connect_printer Exception:",e)

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

    def send_bmp(self):
        try:
            bmp_path = Path("logo.bmp")
            fname = "LOGO.BMP"
            bmp_bytes = bmp_path.read_bytes()
            tspl_after_download = f"""
SIZE 100 mm,29 mm
DIRECTION 1
CLS
PUTBMP 0,0,"{fname}"
PRINT 1
""".lstrip().encode("ascii")
            header = f'DOWNLOAD "{fname}",{len(bmp_bytes)},'.encode("ascii")
            self.socket.sendall(header + bmp_bytes + b"\n")
            # 2) Etikete yerleştir ve yazdır
            self.socket.sendall(tspl_after_download)
        except Exception as e:
            print("send_test Exception:",e)

# Test kodu kaldırıldı - artık Application sınıfı üzerinden kullanılacak
