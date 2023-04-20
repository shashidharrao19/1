from cryptography.hazmat.primitives import hashes 
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key

import requests, base64, os, argparse, sys

import pandas as pd

# Reading sample ppg data
df = pd.read_csv("bidmc_01_Signals.csv")
t_ref = df['Time [s]'].to_numpy()
# ecg = df[' II'].to_numpy()
ppg = df[' PLETH'].to_numpy()
# ppg = df[]

# Creating a time-series collection with first 4 secs of data i.e. 2000 samples
# [TODO] Send and Recieve encrypted data*


# The API endpoint
id = "642d179d4db974333cb95a39"
url_post = "http://127.0.0.1:8000/userdata/"
url_get = f"http://127.0.0.1:8000/{id}"

# Client key file
client_key_file = "client_keys.pem"

# KeyGen
def gen_key():
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048
    )
    return private_key

# Save Key
def save_key(pk, filename):
    pem = pk.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open(filename, 'wb') as pem_out:
        pem_out.write(pem)

# Load Key
def load_key(filename):
    with open(filename, 'rb') as pem_in:
        pemlines = pem_in.read()
    private_key = load_pem_private_key(pemlines, None)
    return private_key

def data_encrpyt(message: str, client_key):
    # Encoding in bytes
    ciphertext = client_key.public_key().encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Encoding to b64 and then decoding bytes to into utf-8 characters
    ciphertext = base64.b64encode(ciphertext) 
    ciphertext = ciphertext.decode('utf-8')
    

    return ciphertext

def data_decrypt(ciphertext: str, client_key):
    # Encoding utf-8 data to b64 byte data, followed by decoding to original bytes data
        # data_b64bytes = ciphertext.encode('utf-8')
        data_cipher = base64.b64decode(ciphertext)

        # Decrypting bytes data
        plaintext = client_key.decrypt(
            data_cipher,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return plaintext




if __name__ == '__main__':
    if not os.path.exists(client_key_file):
        print("Creating new pvt-pub key pair...")
        client_key = gen_key()
        save_key(client_key, client_key_file)
        print("Created")
    else:
        client_key = load_key(client_key_file)
        print(f"Loaded from{client_key_file}")
    # save_key_bad(pk, filename)
    # pk3 = load_key(filename)
    # Creating message with bytes
    message = b"Super Secret PPG Data"

    ciphertext = data_encrpyt(message, client_key)

    # Extracting publickey
    public_pem = client_key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    b64_pubkey = base64.b64encode(public_pem).decode('utf-8')
    
    # print(f"pubkey={b64_pubkey}")

    user_data = {
        "name": "Nikhil",
        "sensor_id": [1],
        "pub_key": b64_pubkey
    }


    # print(user_data)
    # A POST request to the API
    if 'post' in sys.argv:
        print("posting user data")
        response = requests.post(url_post, json=user_data)
        print(response.json())
        
    # A GET request to API to verify data has been posted
    if 'get' in sys.argv:
        print(f"Requesting data")
        response = requests.get(url_get)
        response_json = response.json()
        print(response_json)
        data = response_json['data']

        print("Data Recieved")

    # 
    # response = requests.get(url_get)

    # Extracting data from response
    # response_json = response.json()
    # data = response_json['data']

        plaintext = data_decrypt(data, client_key)

        print(plaintext)
    
    if 'delete' in sys.argv:
        response = requests.delete(url_get)

        print(f"{id} deleted")

