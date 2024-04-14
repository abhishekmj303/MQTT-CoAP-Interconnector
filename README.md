# Abstract of the Project

The Internet of Things (IoT) ecosystem consists of a wide variety of heterogeneous devices using different communication protocols. This can lead to interoperability issues, hindering seamless data exchange between devices. The proposed project aims to develop an interoperability solution, called the MQTT-CoAP Interconnector (MCI), to enable communication between devices using two popular IoT protocols: Message Queuing Telemetry Transport (MQTT) and Constrained Application Protocol (CoAP).

MCI acts as a bridge between the MQTT broker and CoAP server, facilitating data exchange between MQTT's publish-subscribe model and CoAP's request-response model. The core functionality includes parsing and converting messages from one protocol format to the other, minimizing overhead through a compact 2-byte header.

The project will involve designing and implementing the MCI system using open-source technologies and programming languages like Python. The MCI data parser will extract message payloads, convert them to the recipient's protocol format, and handle fragmentation if required. Appropriate acknowledgment mechanisms will ensure reliable message delivery.

The project aims to deliver a lightweight and efficient interoperability solution for resource-constrained IoT devices, enabling seamless communication across heterogeneous platforms. Successful implementation of MCI can contribute to resolving a significant challenge in the IoT ecosystem, fostering interoperability and facilitating the integration of diverse IoT applications and services.

# Setup

## Install Required Libraries

```bash
pip install -r requirements.txt
```

# Usage

## Configuration

- Update the `config.json` file with the appropriate MQTT and CoAP server details.

```json
{
    "mqtt_broker": ["mqtt.eclipseprojects.io", 1883],
    "coap_server": ["127.0.0.1", 5683],
    "mci_server": ["127.0.0.1", 5684],
    "coap_to_mqtt": [ // Listen to CoAP requests and publish or subscribe to MQTT topics
        {
            "mqtt_topic": "light_control",
            "coap_resource": "light_control",
            "methods": ["POST"]
        },
        {
            "mqtt_topic": "light_status",
            "coap_resource": "light_status",
            "methods": ["GET"]
        }
    ],
    "mqtt_to_coap": [ // Subscribe to MQTT topics and POST to CoAP resources
        {
            "mqtt_topic": "light_control",
            "coap_resource": "light_control"
        }
    ]
}
```

## Running the MCI

```bash
python mci.py
```

# Testbed

## Install Tkinter

- For Ubuntu/Debian-based systems:
```bash
sudo apt-get install python3-tk
```

- For Fedora:
```bash
sudo dnf install python3-tkinter
```

- For Arch Linux:
```bash
sudo pacman -S tk
```

- For macOS:
```bash
brew install python-tk
```

## Light connected to local MQTT broker

Yellow light glows when switch is ON and turns black when switch is OFF.

```bash
python testbed/mqtt_light.py
```

## Application to control light using CoAP

App contains a switch to control the light and a status indicator to show the current state of the light.

```bash
python testbed/coap_app.py
```