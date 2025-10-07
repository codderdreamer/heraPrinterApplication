import sys
import os

# Add the current directory to Python path for PyInstaller compatibility
if getattr(sys, 'frozen', False):
    # Running as compiled exe
    application_path = os.path.dirname(sys.executable)
    backend_path = application_path  # Backend modules are in the same directory as exe
else:
    # Running as script
    application_path = os.path.dirname(os.path.abspath(__file__))
    backend_path = os.path.join(application_path, 'backend')

sys.path.insert(0, application_path)
sys.path.insert(0, backend_path)

try:
    from backend.databaseModule.printers import Printers
    from backend.flaskModule import FlaskModule
    from backend.tscPrinterModule import TSCPrinter
except ImportError as e:
    print(f"First import attempt failed: {e}")
    try:
        # Fallback imports for PyInstaller
        from databaseModule.printers import Printers
        from flaskModule import FlaskModule
        from tscPrinterModule import TSCPrinter
        print("Fallback imports successful")
    except ImportError as e2:
        print(f"Fallback import error: {e2}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Python path: {sys.path}")
        print(f"Files in current directory: {os.listdir('.')}")
        if getattr(sys, 'frozen', False):
            print(f"Files in exe directory: {os.listdir(os.path.dirname(sys.executable))}")
        raise

import time

class Application:
    def __init__(self):
        self.printers = Printers()
        self.flaskModule = FlaskModule(self)
        
    def run(self):
        self.flaskModule.run()


if __name__ == "__main__":
    app = Application()
    while True:
        time.sleep(1)
