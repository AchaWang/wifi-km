import os
import sys
import socket
import json
import uvicorn
import qrcode
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Key

app = FastAPI()

mouse = MouseController()
keyboard = KeyboardController()

# Handle PyInstaller path resolution for static files
if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

static_dir = os.path.join(base_dir, "static")

# Provide static files
app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Mobile device connected via WebSocket.")
    try:
        while True:
            data = await websocket.receive_text()
            try:
                cmd = json.loads(data)
                cmd_type = cmd.get("type")
                
                if cmd_type == "move":
                    dx = cmd.get("dx", 0)
                    dy = cmd.get("dy", 0)
                    mouse.move(dx, dy)
                elif cmd_type == "click":
                    button = cmd.get("button", "left")
                    if button == "left":
                        mouse.click(Button.left)
                    elif button == "right":
                        mouse.click(Button.right)
                elif cmd_type == "scroll":
                    dx = cmd.get("dx", 0)
                    dy = cmd.get("dy", 0)
                    # pynput mouse scroll needs to know direction, dy > 0 is scroll up
                    mouse.scroll(dx, dy)
                elif cmd_type == "type_text":
                    text_val = cmd.get("text", "")
                    if text_val:
                        keyboard.type(text_val)
                elif cmd_type == "key":
                    key_val = cmd.get("key")
                    if key_val == "Backspace":
                        keyboard.press(Key.backspace)
                        keyboard.release(Key.backspace)
                    elif key_val == "Enter":
                        keyboard.press(Key.enter)
                        keyboard.release(Key.enter)
                    else:
                        keyboard.type(key_val)
            except json.JSONDecodeError:
                pass
            except Exception as e:
                print(f"Error handling command: {e}")
    except WebSocketDisconnect:
        print("Mobile device disconnected.")

def main():
    ip = get_local_ip()
    port = 8000
    url = f"http://{ip}:{port}/static/"
    
    print("\n" + "="*50)
    print(f"Server is running!")
    print(f"Connect manually at: {url}")
    print("Or scan this QR code with your phone:")
    print("="*50 + "\n")
    
    qr = qrcode.QRCode()
    qr.add_data(url)
    qr.make(fit=True)
    # Generate an image and open it in the default OS image viewer
    img = qr.make_image(fill_color="black", back_color="white")
    img.show()

    # Pass the app object directly instead of a string "main:app" for PyInstaller compatibility
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

if __name__ == "__main__":
    main()
