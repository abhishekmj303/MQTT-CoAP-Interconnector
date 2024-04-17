import tkinter as tk
import time
import threading
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

LIGHT = 0
STATUS = {0: "OFF", 1: "ON"}
COLOR = {0: "black", 1: "yellow"}

def on_message(client, userdata, msg):
    global LIGHT
    if msg.topic != "light_control":
        return
    payload = msg.payload.decode("utf-8").upper()
    if payload == "TOGGLE":
        LIGHT = 1 - LIGHT
    elif payload == "ON":
        LIGHT = 1
    elif payload == "OFF":
        LIGHT = 0
    else:
        print("Invalid message payload")
        return
    
    print(f"Received message: {payload}")
    window.configure(bg=COLOR[LIGHT])


def publish_light_status():
    global LIGHT
    while True:
        client.publish("light_status", STATUS[LIGHT])
        time.sleep(0.1)


client = mqtt.Client(CallbackAPIVersion.VERSION2)
client.on_message = on_message

client.connect("mqtt.eclipseprojects.io", 1883, 60)
client.subscribe("light_control")
client.loop_start()

publish_thread = threading.Thread(target=publish_light_status)
publish_thread.start()

window = tk.Tk()
window.option_add("*Font", "Helvetica 24")
window.title("Room Light")
window.geometry("100x100")

for _ in range(2):
    tk.Label(window, text="", fg="#fff").pack()

app_label = tk.Label(window, text="MQTT Connected Light")
app_label.pack()

# background color will change based on the light status
window.configure(bg=COLOR[LIGHT])

try:
    window.mainloop()
except KeyboardInterrupt:
    print("Exiting...")
    window.destroy()
finally:
    exit()