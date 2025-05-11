from flask import Flask
from threading import Thread
import os

import token

app = Flask(__name__)


@app.route('/')
def home():
    return f"© Wump Development 2025"


def run():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    server = Thread(target=run)
    server.start()

