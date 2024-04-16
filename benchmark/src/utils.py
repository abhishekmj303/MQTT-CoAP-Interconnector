import os
import time
from datetime import datetime
import pandas as pd

SIZES = [64, 128, 256, 512, 1024]

def time_to_payload(t, size):
    timestamp = "{:.7f}".format(t) + "0" * (size - 18)
    return timestamp

def payload_to_time(payload):
    return float(payload[:18])

def save_benchmark_data(suffix, data: pd.DataFrame):
    if len(data) == 0:
        return
    folder = 'benchmark'
    if not os.path.exists(folder):
        os.mkdir(folder)
    df = pd.DataFrame(data)
    df.to_csv(f'{folder}/{suffix}_{datetime.now()}.csv', index=False)
