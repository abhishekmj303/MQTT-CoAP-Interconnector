import time
from coapthon.server.coap import CoAP
from coapthon.resources.resource import Resource
from utils import *

benchmark_data = []

class CoAPResource(Resource):
    def __init__(self, name="CoAPResource", coap_server=None):
        super(CoAPResource, self).__init__(name, coap_server, visible=True,
                                                observable=True, allow_children=True)
        self.payload = b""
    
    def render_POST(self, request):
        t2 = time.time()
        s = len(request.payload)
        t1 = payload_to_time(request.payload)
        t = t2 - t1
        benchmark_data.append({"size": s, "time": t})
        return self

class CoAPServer(CoAP):
    def __init__(self):
        CoAP.__init__(self, ("127.0.0.1", 5683))
        self.add_resource("benchmark", CoAPResource())

if __name__ == "__main__":
    server = CoAPServer()
    try:
        server.listen(10)
    except KeyboardInterrupt:
        print("Server Shutdown")
        server.close()
        print("Exiting...")
        save_benchmark_data("m2c", benchmark_data)
