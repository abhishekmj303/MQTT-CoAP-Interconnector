import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
import time

def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode('utf-8')}")

client = mqtt.Client(CallbackAPIVersion.VERSION2)
client.on_message = on_message

client.connect("mqtt.eclipseprojects.io", 1883, 60)

while True:
    client.publish("my/topic", f"Hello, world! {time.time()}")
    print("Published message")
    time.sleep(2)