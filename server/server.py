from flask import Flask
from flask_socketio import SocketIO
from dotenv import load_dotenv
import os

socketio = SocketIO(cors_allowed_origins = "*")

load_dotenv()
HOST = os.getenv("HOST", "0.0.0.0")
PORT = os.getenv("PORT", 8888)
MODEL = os.getenv("MODEL", "deepseek-r1:7b")
MODEL_URL = os.getenv("MODEL_URL", "127.0.0.1:11434")

def start():
    app = Flask(__name__)
    socketio.init_app(app)

    from server.api.ws import register_event
    register_event(socketio)

    socketio.run(app, HOST, int(PORT))

if __name__ == "__main__":
    start()
