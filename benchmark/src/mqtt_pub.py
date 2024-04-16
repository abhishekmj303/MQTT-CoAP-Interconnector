import time
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
from utils import *

client = mqtt.Client(CallbackAPIVersion.VERSION2)
client.connect("mqtt.eclipseprojects.io", 1883, 60)


for _ in range(200):
    for s in SIZES:
        payload = time_to_payload(time.time(), s)
        client.publish("benchmark", payload)
        time.sleep(0.1)