import tkinter as tk
import time
import threading
from coapthon.server.coap import CoAP
from coapthon.resources.resource import Resource
import coapthon.client.helperclient as CoAPClient

import json
from pydantic import ValidationError
import sys
sys.path.append(".")
from config_model import Config

CONFIG: Config

class CoAPResource(Resource):
    def __init__(self, methods, name="CoAPResource", coap_server=None):
        super(CoAPResource, self).__init__(name, coap_server, visible=True,
                                                observable=True, allow_children=True)
        self.payload = b""
        self.client = CoAPClient.HelperClient(CONFIG.mci_server)
        self.methods = methods

    def render_GET(self, request):
        if "GET" not in self.methods:
            raise NotImplementedError
        
        print("Received CoAP GET request on", request.uri_path)
        response = self.client.get(request.uri_path)
        self.payload = response.payload
        return self

    def render_POST(self, request):
        if "POST" not in self.methods:
            raise NotImplementedError
        
        print(f"Received CoAP POST request on {request.uri_path}: {request.payload}")
        self.payload = b"POST request received"
        return self

class CoAPServer(CoAP):
    def __init__(self):
        global CONFIG
        try:
            with open("config.json", "r") as config_file:
                config_data = config_file.read()
            CONFIG = Config(**json.loads(config_data))
            print(CONFIG)
        except (FileNotFoundError, ValidationError) as e:
            print("Error loading configuration file:", e)
            exit(1)
        
        CoAP.__init__(self, CONFIG.coap_server)
        for mapping in CONFIG.coap_to_mqtt:
            self.add_resource(mapping.coap_resource, CoAPResource(mapping.methods))


def toggle_light():
    client.post("light_control", "toggle")

def update_status():
    while True:
        response = client.get("light_status")
        if response.payload:
            status_label.config(text=f"Light Status: {response.payload.upper()}")
        else:
            status_label.config(text="Light Status: Unknown")
        time.sleep(0.1)

server = CoAPServer()
server_thread = threading.Thread(target=server.listen, args=(10,))
server_thread.start()

client = CoAPClient.HelperClient(("127.0.0.1", 5684))

window = tk.Tk()
# increase font size
window.option_add("*Font", "Helvetica 24")
window.title("Room Light Control")

status_label = tk.Label(window, text="Light Status: Unknown")
status_label.pack()

toggle_button = tk.Button(window, text="Toggle Light", command=toggle_light)
toggle_button.pack()

for _ in range(3):
    tk.Label(window, text="").pack()

app_label = tk.Label(window, text="CoAP Client App")
app_label.pack()

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