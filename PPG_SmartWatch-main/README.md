# IoT SmartWatch Server Implementation

## Getting Started 

Install Dependencies via

`pip install -r requirments.txt`

Run the development server using

`uvicorn main:app --reload`

The code uses FastApi for backend, and relies on MongoDB for storage. It is currently configured on the free test instance provided by [MongoDB Cloud](https://www.mongodb.com/cloud), so once you get your creds, modify `creds_sample.json` and rename the file as `creds.json`

## Basic Idea

The aim of the code is to replicate the structure in [this paper](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4801556/). Few liberties have to be taken as we will be preprocessing the data before sending it to the users(patient/doctor)

![System Model](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4801556/bin/sensors-16-00179-g002.jpg)

Data needs to be encrypted from the watch itself, accesible only to users authorised to the data.

## Current Implementation

Currently, as a PoC, we are using RSA Key Pairs, wherein there are 2 keys involved - the public key and the private key. The user gives away his public key to the device, which then encrypts the data via public key that gets stored inside the server. The server has two collections:
* User: Saves user data such as public key and the sensors authorised
* sensor: Stores encrypted sensor data

For saving sensor data, rather than encrypt every single value, 20 values are taken at a time and then encrypted. This is sent to the server where it is saved with a timestamp. 

If you do not have an RSA key pair on your device, a key pair is automatically created

## [TODO] Dev Goals
1) FindOne with sensor number and timestamp
2) HTTPS and TLS for requests
3) Auth implementation to prevent unauthorised people from writing to server with data
4) Auth on Registration process
