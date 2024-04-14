from coapthon.server.coap import CoAP
from coapthon.resources.resource import Resource

class HelloWorldResource(Resource):
    def __init__(self, name="HelloWorldResource", coap_server=None):
        super(HelloWorldResource, self).__init__(name, coap_server, visible=True,
                                                observable=True, allow_children=True)
        self.payload = "Hello World!"

    def render_GET(self, request):
        return self

    def render_POST(self, request):
        print(f"Received message: {request.payload}")
        self.payload = request.payload
        return self

class CoAPServer(CoAP):
    def __init__(self, host, port):
        CoAP.__init__(self, (host, port))
        self.add_resource('/', HelloWorldResource())

if __name__ == '__main__':
    server = CoAPServer("127.0.0.1", 5683)
    try:
        print("CoAP Server started")
        server.listen(10)
    except KeyboardInterrupt:
        print("CoAP Server Shutdown")
        server.close()
        print("Exiting...")