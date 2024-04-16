import time
import pandas as pd
import coapthon.client.helperclient as CoAPClient
from utils import *

client = CoAPClient.HelperClient(server=("127.0.0.1", 5684))

for _ in range(200):
    for s in SIZES:
        payload = time_to_payload(time.time(), s)
        response = client.post("benchmark", payload)
        time.sleep(0.1)