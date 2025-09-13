from backend.databaseModule.printers import Printers
from backend.flaskModule import FlaskModule
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
