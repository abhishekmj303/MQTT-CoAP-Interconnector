import tkinter as tk
import time
import threading
import coapthon.client.helperclient as CoAPClient
from coap_server import CoAPServer

def toggle_light():
    client.post("light_control", "toggle")

def update_status():
    while True:
        response = client.get("light_status")
        status_label.config(text=f"Light Status: {response.payload.upper()}")
        time.sleep(5)

server = CoAPServer()
server_thread = threading.Thread(target=server.listen, args=(10,))
server_thread.start()

client = CoAPClient.HelperClient(("127.0.0.1", 5683))

window = tk.Tk()
window.title("Room Light Control")

status_label = tk.Label(window, text="Light Status: OFF")
status_label.pack()

toggle_button = tk.Button(window, text="Toggle Light", command=toggle_light)
toggle_button.pack()

update_thread = threading.Thread(target=update_status)
update_thread.start()

try:
    window.mainloop()
except KeyboardInterrupt:
    print("Exiting...")
    window.destroy()
finally:
    server.close()
    server_thread.join()