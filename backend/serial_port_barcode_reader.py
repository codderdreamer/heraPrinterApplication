import serial
import serial.tools.list_ports
import threading
import time
import requests
from typing import Optional, Callable

class SerialPortBarcodeReader:
    """Zebra barkod okuyucu için seri port okuma modülü"""
    
    def __init__(self, port: Optional[str] = None, baudrate: int = 9200, callback: Optional[Callable] = None):
        """
        Args:
            port: Seri port adı (örn: 'COM3'). None ise otomatik bulur
            baudrate: Baudrate (varsayılan: 9200)
            callback: Okunan barkod için callback fonksiyonu (barcode_data: str) -> None
        """
        self.port = port
        self.baudrate = baudrate
        self.callback = callback
        self.serial_connection = None
        self.is_reading = False
        self.read_thread = None
        self.api_url = "http://127.0.0.1:8088/api/barcodeScanner/print"
    
    def find_serial_ports(self):
        """Mevcut seri portları listeler"""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    
    def connect(self, port: Optional[str] = None):
        """Seri port bağlantısını açar"""
        try:
            if port:
                self.port = port
            elif not self.port:
                # Otomatik port bulma - COM4'ü öncelikli ara
                ports = self.find_serial_ports()
                if not ports:
                    raise Exception("No serial ports found")
                
                # COM4 varsa onu kullan, yoksa ilk bulunan portu kullan
                if "COM4" in ports:
                    self.port = "COM4"
                    print(f"Auto-detected serial port: {self.port}")
                else:
                    self.port = ports[0]  # İlk bulunan portu kullan
                    print(f"Auto-detected serial port: {self.port} (COM4 not found)")
            
            print(f"Connecting to serial port: {self.port} at {self.baudrate} baudrate")
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False
            )
            
            # Seri portu temizle
            self.serial_connection.reset_input_buffer()
            self.serial_connection.reset_output_buffer()
            
            print(f"Connected to {self.port} successfully")
            return True
        except Exception as e:
            print(f"Error connecting to serial port: {e}")
            return False
    
    def disconnect(self):
        """Seri port bağlantısını kapatır"""
        self.stop_reading()
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            print(f"Disconnected from {self.port}")
    
    def _read_barcode(self):
        """Seri porttan barkod okuma thread fonksiyonu"""
        buffer = ""
        
        while self.is_reading:
            try:
                if self.serial_connection and self.serial_connection.is_open:
                    # Veri varsa oku
                    if self.serial_connection.in_waiting > 0:
                        data = self.serial_connection.read(self.serial_connection.in_waiting)
                        buffer += data.decode('utf-8', errors='ignore')
                        
                        # CR, LF veya Enter karakteri geldiğinde barkod tamamlanmış demektir
                        if '\r' in buffer or '\n' in buffer or '\r\n' in buffer:
                            # Barkodu temizle (CR, LF karakterlerini kaldır)
                            barcode = buffer.strip().replace('\r', '').replace('\n', '')
                            
                            if barcode:
                                print(f"Barcode read: '{barcode}'")
                                self._process_barcode(barcode)
                            
                            buffer = ""  # Buffer'ı temizle
                    else:
                        time.sleep(0.01)  # Kısa bir bekleme
                else:
                    print("Serial port is not open")
                    break
            except Exception as e:
                print(f"Error reading from serial port: {e}")
                time.sleep(0.1)
    
    def _process_barcode(self, barcode_data: str):
        """Okunan barkodu işler"""
        try:
            # Callback varsa çağır
            if self.callback:
                self.callback(barcode_data)
            else:
                # Varsayılan olarak API endpoint'ine gönder
                self._send_to_api(barcode_data)
        except Exception as e:
            print(f"Error processing barcode: {e}")
    
    def _send_to_api(self, serial_number: str):
        """Okunan barkodu API endpoint'ine gönderir"""
        try:
            payload = {"SERIAL_NUMBER": serial_number}
            response = requests.post(self.api_url, json=payload, timeout=5)
            if response.status_code == 200:
                print(f"Barcode '{serial_number}' sent to API successfully")
            else:
                print(f"API error: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error sending barcode to API: {e}")
    
    def start_reading(self):
        """Barkod okumayı başlatır"""
        if not self.serial_connection or not self.serial_connection.is_open:
            if not self.connect():
                return False
        
        if not self.is_reading:
            self.is_reading = True
            self.read_thread = threading.Thread(target=self._read_barcode, daemon=True)
            self.read_thread.start()
            print("Barcode reading started")
            return True
        return False
    
    def stop_reading(self):
        """Barkod okumayı durdurur"""
        if self.is_reading:
            self.is_reading = False
            if self.read_thread:
                self.read_thread.join(timeout=2)
            print("Barcode reading stopped")
    
    def is_connected(self):
        """Seri port bağlantısının durumunu kontrol eder"""
        return self.serial_connection is not None and self.serial_connection.is_open


if __name__ == "__main__":
    """Tek başına çalıştırıldığında seri port barkod okuyucuyu başlatır"""
    import sys
    
    # Port argümanı al (opsiyonel)
    port = None
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    print("=" * 50)
    print("Zebra Serial Port Barcode Reader")
    print("=" * 50)
    
    # Seri port barkod okuyucuyu oluştur
    reader = SerialPortBarcodeReader(port=port, baudrate=9200)
    
    # Mevcut portları listele
    print("\nAvailable serial ports:")
    ports = reader.find_serial_ports()
    if ports:
        for p in ports:
            print(f"  - {p}")
    else:
        print("  No serial ports found")
    
    # Bağlan ve okumayı başlat
    if reader.connect():
        print(f"\nConnected to {reader.port} at {reader.baudrate} baudrate")
        if reader.start_reading():
            print("Barcode reading started. Press Ctrl+C to stop.")
            print("Waiting for barcodes...\n")
            
            try:
                # Ana döngü - Ctrl+C ile durdurulabilir
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\nStopping barcode reader...")
                reader.stop_reading()
                reader.disconnect()
                print("Barcode reader stopped.")
        else:
            print("Failed to start reading")
            reader.disconnect()
    else:
        print("Failed to connect to serial port")
        sys.exit(1)
