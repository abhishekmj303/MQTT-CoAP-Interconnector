# Abstract of the Project

The Internet of Things (IoT) ecosystem consists of a wide variety of heterogeneous devices using different communication protocols. This can lead to interoperability issues, hindering seamless data exchange between devices. The proposed project aims to develop an interoperability solution, called the MQTT-CoAP Interconnector (MCI), to enable communication between devices using two popular IoT protocols: Message Queuing Telemetry Transport (MQTT) and Constrained Application Protocol (CoAP).

MCI acts as a bridge between the MQTT broker and CoAP server, facilitating data exchange between MQTT's publish-subscribe model and CoAP's request-response model. The core functionality includes parsing and converting messages from one protocol format to the other, minimizing overhead through a compact 2-byte header.

The project will involve designing and implementing the MCI system using open-source technologies and programming languages like Python. The MCI data parser will extract message payloads, convert them to the recipient's protocol format, and handle fragmentation if required. Appropriate acknowledgment mechanisms will ensure reliable message delivery.

The project aims to deliver a lightweight and efficient interoperability solution for resource-constrained IoT devices, enabling seamless communication across heterogeneous platforms. Successful implementation of MCI can contribute to resolving a significant challenge in the IoT ecosystem, fostering interoperability and facilitating the integration of diverse IoT applications and services.
