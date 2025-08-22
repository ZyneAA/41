import os
import requests

from server.server import MODEL_URL, MODEL

async def stream_tokens(prompt: str, model = MODEL):

    url = f"{MODEL_URL}/generate"
    payload = {"model": model, "prompt": prompt, "stream": True}

    with requests.post(url, json = payload, stream = True) as r:
        for line in r.iter_lines():
            if line:
                try:
                    data = line.decode("utf-8")
                    yield data
                except Exception:
                    continue
