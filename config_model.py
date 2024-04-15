from pydantic import BaseModel
from typing import List, Tuple

class CoAP2MQTT(BaseModel):
    mqtt_topic: str
    coap_resource: str
    methods: List[str]

class MQTT2CoAP(BaseModel):
    coap_resource: str
    mqtt_topic: str

class Config(BaseModel):
    mqtt_broker: Tuple[str, int]
    coap_server: Tuple[str, int]
    mci_server: Tuple[str, int]
    coap_to_mqtt: List[CoAP2MQTT]
    mqtt_to_coap: List[MQTT2CoAP]