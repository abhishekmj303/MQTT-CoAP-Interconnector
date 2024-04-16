import time
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
from utils import *

benchmark_data = []

def on_message(client, userdata, msg):
    t2 = time.time()
    s = len(msg.payload)
    t1 = payload_to_time(msg.payload)
    t = t2 - t1
    benchmark_data.append({"size": s, "time": t})

client = mqtt.Client(CallbackAPIVersion.VERSION2)
client.on_message = on_message
client.connect("mqtt.eclipseprojects.io", 1883, 60)

client.subscribe("benchmark")
try:
    client.loop_forever()
except KeyboardInterrupt:
    print("Exiting...")
    save_benchmark_data("c2m", benchmark_data)