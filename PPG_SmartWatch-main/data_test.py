import pandas as pd
import numpy as np

import crypto

import datetime, requests
t_stamp = datetime.datetime.now().isoformat()
# print(type(t_stamp))

# Client key file
client_key_file = "client_keys.pem"

# The API endpoint
id = "642d179d4db974333cb95a39"

sensor_id = 1
url_post_userdata = "http://127.0.0.1:8000/userdata/"
url_post_sensordata = "http://127.0.0.1:8000/sensordata/"
# url_get = f"http://127.0.0.1:8000/{id}"

# Reading sample ppg data
df = pd.read_csv("bidmc_01_Signals.csv")
t_ref = df['Time [s]'].to_numpy()
# ecg = df[' II'].to_numpy()
ppg = df[' PLETH'].to_numpy()
# print(t_ref[0])
count = 20
data_slice = ppg[0:count]
data_slice_str = bytes(np.array_str(data_slice, max_line_width=1000000).strip('[]'),'utf-8')
# print(np.array_str(data_slice))
# print(data_slice_str.decode())

crypto_key = crypto.load_key(client_key_file)

data_encrypted = crypto.data_encrpyt(data_slice_str, crypto_key)

sensor_data = {
        "timeseries": {
            "timeField": t_stamp,
            "metaField": {
                "sensor_id":sensor_id, 
                "SensorType":"HeartBeat"
            },
            "granularity":"seconds",
            "data":data_encrypted
        }
    }

data_decrypted = crypto.data_decrypt(data_encrypted, crypto_key)

# print(data_decrypted.decode())
ppg_decrypted = np.fromstring(data_decrypted, count=count, sep=' ', dtype=float)

print("posting sensor data")
response = requests.post(url_post_sensordata, json=sensor_data)
print(response.json())

# print(ppg_decrypted)