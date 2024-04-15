# MQTT
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

# CoAP
import coapthon
from coapthon.server.coap import CoAP
from coapthon.resources.resource import Resource
import coapthon.client.helperclient as CoAPClient

# Standard library
import struct
import time
import threading

# JSON configuration
import json
from json.decoder import JSONDecodeError
from pydantic import ValidationError
from config_model import Config

MTU = 1500  # Maximum Transfer Unit


class MCI:
    def __init__(self):
        # Mappings
        self.coap_resource = {m.mqtt_topic: m.coap_resource for m in CONFIG.mqtt_to_coap}
        self.mqtt_topic = {m.coap_resource: m.mqtt_topic for m in CONFIG.coap_to_mqtt}
        self.mqtt_previous_message = {m.mqtt_topic: None for m in CONFIG.coap_to_mqtt}

        # MQTT interface
        self.mqtt_client = mqtt.Client(CallbackAPIVersion.VERSION2)
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message

        # CoAP interface
        self.coap_client = CoAPClient.HelperClient(CONFIG.coap_server)
        self.coap_listener = CoAPServer(CONFIG.mci_server, self)

    def on_mqtt_connect(self, client, userdata, flags, rc, properties=None):
        print("Connected to MQTT broker with result code " + str(rc))
        for mapping in CONFIG.mqtt_to_coap:
            self.mqtt_client.subscribe(mapping.mqtt_topic)
        for mapping in CONFIG.coap_to_mqtt:
            if "GET" in mapping.methods:
                self.mqtt_client.subscribe(mapping.mqtt_topic)

    def on_mqtt_message(self, client, userdata, msg):
        print("Received MQTT message on topic " + msg.topic)
        if msg.topic in self.coap_resource:
            threading.Thread(target=self.process_mqtt_message, args=(msg.topic, msg.payload)).start()
        else:
            self.mqtt_previous_message[msg.topic] = msg.payload

    def process_mqtt_message(self, topic, payload):
        # Extract message payload and topic from MQTT message
        coap_payload = payload
        coap_resource = self.coap_resource[topic]

        # If the CoAP payload is greater than the MTU, fragment it
        if len(coap_payload) > MTU:
            # Encapsulate the message in the CoAP packet format with a 2-byte header (sequence number)
            mtu = MTU - 2
            sequence_number = 0
            transmission_history = []
            fragments = [coap_payload[i:i+mtu] for i in range(0, len(coap_payload), mtu)]
            for fragment in fragments:
                sequence_number += 1
                header = struct.pack("!H", sequence_number)
                self.send_coap_message(coap_resource, header + bytes(fragment))
                transmission_history.append((topic, fragment, time.time()))
                if len(transmission_history) > 100:
                    transmission_history.pop(0)
        else:
            self.send_coap_message(coap_resource, coap_payload)

    def send_coap_message(self, resource, payload):
        response = self.coap_client.post(resource, payload)
        if response.code == coapthon.defines.Codes.CHANGED.number:
            print(f"CoAP message sent successfully: {resource}")
        else:
            print(f"Failed to send CoAP message: {resource}")

    def start(self):
        self.coap_listener_thread = threading.Thread(target=self.coap_listener.listen, args=(10,))
        self.coap_listener_thread.start()
        print("CoAP server listening on port", CONFIG.mci_server[1])

        self.mqtt_client.connect(*CONFIG.mqtt_broker, 60)
        self.mqtt_client.loop_forever()


class CoAP_GET(Resource):
    def __init__(self, mci: MCI, mqtt_topic, coap_server=None):
        super(CoAP_GET, self).__init__(mqtt_topic, coap_server, visible=True,
                                            observable=True, allow_children=True)
        self.payload = b""
        self.mci = mci
        self.mqtt_topic = mqtt_topic

    def render_GET(self, request):
        print("Received CoAP GET request on", request.uri_path)
        self.payload = self.mci.mqtt_previous_message[self.mqtt_topic]
        if self.payload is None:
            self.payload = b""
        print(f"Returning message: {self.payload}")
        return self


class CoAP_POST(Resource):
    def __init__(self, mci: MCI, mqtt_topic, coap_server=None):
        super(CoAP_POST, self).__init__(mqtt_topic, coap_server, visible=True,
                                            observable=True, allow_children=True)
        self.payload = b""
        self.mci = mci
        self.mqtt_topic = mqtt_topic

    def render_POST(self, request):
        print(f"Received CoAP POST request on {request.uri_path}: {request.payload}")
        msginfo = self.mci.mqtt_client.publish(self.mqtt_topic, request.payload)
        if msginfo.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"Published MQTT message to {self.mqtt_topic}: {request.payload}")
        else:
            print(f"Failed to publish message to {self.mqtt_topic}: {request.payload}")
        return self


class CoAPServer(CoAP):
    def __init__(self, address, mci):
        CoAP.__init__(self, address)
        for mapping in CONFIG.coap_to_mqtt:
            if "GET" in mapping.methods:
                self.add_resource(mapping.coap_resource, CoAP_GET(mci, mci.mqtt_topic[mapping.coap_resource]))
            if "POST" in mapping.methods:
                self.add_resource(mapping.coap_resource, CoAP_POST(mci, mci.mqtt_topic[mapping.coap_resource]))
        self.mci = mci


if __name__ == "__main__":
    try:
        with open("config.json", "r") as config_file:
            config_data = config_file.read()
        CONFIG = Config(**json.loads(config_data))
        print(CONFIG)
    except (FileNotFoundError, JSONDecodeError, ValidationError) as e:
        print(f"Error loading configuration file: {e.__class__.__name__}: {e}")
        exit(1)

    mci = MCI()
    mci.start()