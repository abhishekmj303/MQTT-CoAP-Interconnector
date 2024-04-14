import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
import coapthon
from coapthon.server.coap import CoAP
from coapthon.resources.resource import Resource
import coapthon.client.helperclient as CoAPClient
import struct
import time
import threading
import json
from pydantic import ValidationError
from json_config import Config

MTU = 1500  # Maximum Transfer Unit

class CoAPResource(Resource):
    def __init__(self, mci, name="CoAPResource", coap_server=None):
        super(CoAPResource, self).__init__(name, coap_server, visible=True,
                                            observable=True, allow_children=True)
        self.payload = b""
        self.mci = mci

    def render_GET(self, request):
        print("Received GET request")
        print(request.uri_path)
        return self
    
    def render_PUT(self, request):
        return self

    def render_POST(self, request):
        print(f"Received message: {request.payload}")
        self.payload = request.payload
        return self
    
    def render_DELETE(self, request):
        return True


class CoAPServer(CoAP):
    def __init__(self, address, mci):
        CoAP.__init__(self, address)
        self.add_resource('/hello', CoAPResource(mci))
        self.mci = mci

class MCI:
    def __init__(self, mqtt_broker_address, mqtt_topic, coap_server_address, coap_resource):
        self.mqtt_client = mqtt.Client(CallbackAPIVersion.VERSION2)
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        self.mqtt_broker_address = mqtt_broker_address
        self.mqtt_topic = mqtt_topic
        self.coap_client = CoAPClient.HelperClient(server=(coap_server_address, 5683))
        self.coap_listener = CoAPServer(("127.0.0.1", 5684), self)
        self.coap_listener_thread = threading.Thread(target=self.coap_listener.listen, args=(10,))
        self.coap_listener_thread.start()
        self.coap_resource = coap_resource
        self.sequence_number = 0
        self.transmission_history = []

    def on_mqtt_connect(self, client, userdata, flags, rc, properties=None):
        print("Connected to MQTT broker with result code " + str(rc))
        self.mqtt_client.subscribe(self.mqtt_topic)

    def on_mqtt_message(self, client, userdata, msg):
        print("Received MQTT message on topic " + msg.topic)
        self.process_mqtt_message(msg.topic, msg.payload)

    def process_mqtt_message(self, topic, payload):
        # Extract message payload and topic from MQTT message
        message_data = payload
        message_subject = topic

        # Encapsulate the message in the CoAP packet format with a 2-byte header
        header = struct.pack('!H', self.sequence_number)
        coap_payload = header + message_data
        self.sequence_number += 1
        print(coap_payload)

        # If the CoAP payload is greater than the MTU, fragment it
        if len(coap_payload) > MTU:
            fragments = [coap_payload[i:i+MTU] for i in range(0, len(coap_payload), MTU)]
            for fragment in fragments:
                self.send_coap_message(message_subject, fragment)
        else:
            self.send_coap_message(message_subject, coap_payload)

        # Log the transmission
        self.transmission_history.append((topic, payload, time.time()))
        if len(self.transmission_history) > 100:
            self.transmission_history.pop(0)

    def send_coap_message(self, message_subject, payload):
        response = self.coap_client.post(self.coap_resource, payload)
        if response.code == coapthon.defines.Codes.CHANGED.number:
            print(f"CoAP message sent successfully: {message_subject}")
        else:
            print(f"Failed to send CoAP message: {message_subject}")

    # def on_coap
    

    def start(self):
        self.mqtt_client.connect(self.mqtt_broker_address, 1883, 60)
        self.mqtt_client.loop_forever()

if __name__ == "__main__":
    try:
        with open("config.json", "r") as config_file:
            config_data = config_file.read()
        CONFIG = Config(**json.loads(config_data))
        print(CONFIG)
    except (FileNotFoundError, ValidationError) as e:
        print(e, "Error loading configuration file")
        exit(1)

    mci = MCI("mqtt.eclipseprojects.io", "my/topic", "127.0.0.1", "/my-resource")
    mci.start()