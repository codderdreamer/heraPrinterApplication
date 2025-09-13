from backend.configModule import ConfigModule
from backend.databaseModule import DatabaseModule
from backend.databaseQueryModule import DatabaseQueryModule
from backend.flaskModule import FlaskModule


class Application:
    def __init__(self):
        self.config = ConfigModule()
        self.database = DatabaseModule(self.config)
        self.databaseQuery = DatabaseQueryModule()
        self.flask = FlaskModule(self)

    def run(self):
        self.flask.run()


if __name__ == "__main__":
    app = Application()