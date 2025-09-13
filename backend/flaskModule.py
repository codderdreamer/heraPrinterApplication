from flask import Flask, Response, render_template, request, jsonify, session
from threading import Thread

class FlaskModule:
    def __init__(self, application) -> None:
        self.application = application
        self.app = Flask(__name__, static_url_path='',
                         static_folder='../frontend/build',
                         template_folder='../frontend/build')