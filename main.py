from backend.configModule import ConfigModule
from backend.databaseModule.printers import Printers
from backend.flaskModule import FlaskModule


class Application:
    def __init__(self):
        self.config = ConfigModule()
        self.databaseQuery = Printers(self.config.database_path)
        self.flask = FlaskModule(self)

    def run(self):
        self.flask.run()


if __name__ == "__main__":
    app = Application()
