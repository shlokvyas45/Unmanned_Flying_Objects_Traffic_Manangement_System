
import websocket
import threading
import time

def on_message(ws, message):
    print("Telemetry received:", message)

def on_error(ws, error):
    print("WebSocket error:", error)

def on_open(ws):
    print("WebSocket connected")

def on_close(ws, status_code, message):
    print("WebSocket disconnected")

ws = websocket.WebSocketApp(
    "ws://127.0.0.1:8000/ws/telemetry",
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close,
)

thread = threading.Thread(target=ws.run_forever)
thread.start()

time.sleep(2)

try:
    input("WebSocket connected ho toh Enter dabao...")
finally:
    ws.close()
    thread.join(timeout=3)
