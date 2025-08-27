import asyncio
import json
import aiohttp
import websockets

# Configuration for the WebSocket and Ollama servers
WEBSOCKET_HOST = "localhost"
WEBSOCKET_PORT = 8765
OLLAMA_API_URL = "http://localhost:11434/api/generate"

async def ollama_stream_handler(websocket, path):
    """
    Handles a single WebSocket connection, processes a prompt,
    and streams tokens from Ollama back to the client.
    """
    print(f"[{websocket.remote_address}] Connection established. Waiting for prompt...")

    try:
        # Wait for the initial message from the client containing the prompt and model
        message = await websocket.recv()
        data = json.loads(message)
        prompt = data.get("prompt")
        model = data.get("model", "llama2") # Default to llama2 if no model is specified

        if not prompt:
            await websocket.send(json.dumps({"error": "No prompt provided."}))
            return

        print(f"[{websocket.remote_address}] Received prompt for model '{model}': '{prompt[:50]}...'")

        # Prepare the request body for the Ollama API
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True
        }

        # Use aiohttp for an asynchronous HTTP request to the Ollama API
        async with aiohttp.ClientSession() as session:
            try:
                # The timeout prevents hanging if the Ollama server is unresponsive
                async with session.post(OLLAMA_API_URL, json=payload, timeout=300) as response:
                    # Check for a successful response from Ollama
                    if response.status != 200:
                        error_text = await response.text()
                        print(f"[{websocket.remote_address}] Ollama API error: {response.status} - {error_text}")
                        await websocket.send(json.dumps({"error": f"Ollama API error: {response.status}"}))
                        return

                    # Stream the response content line by line
                    async for line in response.content:
                        if line:
                            try:
                                # Ollama streams a JSON object for each token
                                chunk = json.loads(line.decode('utf-8'))
                                token = chunk.get("response", "")
                                await websocket.send(token)
                                
                                # Check if the stream is complete
                                if chunk.get("done", False):
                                    print(f"[{websocket.remote_address}] Stream complete.")
                                    break
                            except json.JSONDecodeError:
                                print(f"[{websocket.remote_address}] Failed to decode JSON chunk: {line.decode('utf-8')}")
                                await websocket.send(f"Error decoding chunk: {line.decode('utf-8')}")
                            except Exception as e:
                                print(f"[{websocket.remote_address}] An unexpected error occurred: {e}")
                                await websocket.send(f"An unexpected error occurred: {e}")

            except aiohttp.ClientError as e:
                print(f"[{websocket.remote_address}] Aiohttp client error: {e}")
                await websocket.send(json.dumps({"error": f"Failed to connect to Ollama API: {e}"}))
            except asyncio.TimeoutError:
                print(f"[{websocket.remote_address}] Connection to Ollama timed out.")
                await websocket.send(json.dumps({"error": "Request to Ollama timed out."}))

    except websockets.exceptions.ConnectionClosed as e:
        print(f"[{websocket.remote_address}] Connection closed with code {e.code}: {e.reason}")
    except json.JSONDecodeError:
        print(f"[{websocket.remote_address}] Received invalid JSON.")
    except Exception as e:
        print(f"[{websocket.remote_address}] An error occurred: {e}")
    finally:
        print(f"[{websocket.remote_address}] Disconnecting...")

async def main():
    """Main function to start the WebSocket server."""
    # Use the `serve` function to create and run the server
    async with websockets.serve(ollama_stream_handler, WEBSOCKET_HOST, WEBSOCKET_PORT):
        print(f"WebSocket server started at ws://{WEBSOCKET_HOST}:{WEBSOCKET_PORT}")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped manually.")
