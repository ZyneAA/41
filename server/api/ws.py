from flask_socketio import emit

from server.server import MODEL
from server.util.generator import generate_char

def register_event(socketio):

    @socketio.on("generate")
    def handle_generate(data):
        prompt = data.get("prompt", "Hello!")
        model = data.get("model", MODEL)

        #
        #
        # ACTUAL LOGIC FOR OLLAMA HEREEEEEEEEE
        #
        #

        for _ in range(1, 1000):
            emit("token", generate_char())

        emit("end", {"status": "done"})
