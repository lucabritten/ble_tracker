import time
from umqtt.simple import MQTTClient
import asyncio
import json
import os

from track_phone import get_rssi_for_device
from utility import load_from_json

CONFIG_FILE = "config/config.json"

SERVER = load_from_json(CONFIG_FILE, "mqtt", "server_ip")
user = load_from_json(CONFIG_FILE, "mqtt", "user_name")
password = load_from_json(CONFIG_FILE, "mqtt", "user_pass")

ClientID = f'raso-sub-{time.time_ns()}'
topic = b"esp/tracking"

def connect():
    print(f'Connected to MQTT Broker {SERVER}')
    client = MQTTClient(ClientID, SERVER, 1883, user, password)
    client.connect()
    return client

def reconnect():
    print(f'Reconnecting to {SERVER}')
    time.sleep(5)
    try:
        client = connect()
        return client
    except OSError:
        return reconnect()