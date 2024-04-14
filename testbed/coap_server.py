from coapthon.server.coap import CoAP
from coapthon.resources.resource import Resource
import coapthon.client.helperclient as CoAPClient

import json
from pydantic import ValidationError
import sys
sys.path.append(".")
from json_config import Config

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
        response = self.client.post(request.uri_path, request.payload)
        # self.payload = response.payload
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

if __name__ == '__main__':
    server = CoAPServer("127.0.0.1", 5683)
    try:
        print("CoAP Server started")
        server.listen(10)
    except KeyboardInterrupt:
        print("CoAP Server Shutdown")
        server.close()
        print("Exiting...")