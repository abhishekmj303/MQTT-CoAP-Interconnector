from pydantic import BaseModel
from typing import List, Tuple

class Mapping(BaseModel):
    mqtt_topic: str
    coap_resource: str

class Config(BaseModel):
    mqtt_broker: Tuple[str, int]
    coap_server: Tuple[str, int]
    coap_to_mqtt: List[Mapping]
    mqtt_to_coap: List[Mapping]