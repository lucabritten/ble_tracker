import json
import aiomqtt

from positioning import calculate_current_location
from utility import load_from_json

CONFIG_FILE = "config/config.json"
BROKER_IP = load_from_json(CONFIG_FILE, "mqtt", "server_ip")
USER_NAME = load_from_json(CONFIG_FILE, "mqtt", "user_name")
PASSWORD = load_from_json(CONFIG_FILE, "mqtt", "user_pass")

latest_rssi_data = {}

async def start_mqtt_listener():
    async with aiomqtt.Client(
        hostname=BROKER_IP,
        username=USER_NAME,
        password=PASSWORD) as client:
        await client.subscribe("esp/tracking")
        print("Raspberry PI listening for ESP signals...")
        
        async for message in client.messages:
            try:
                payload = json.loads(message.payload.decode("utf-8"))
                
                rssi = payload.get("rssi")
                location = payload.get("location")
                
                latest_rssi_data[location] = rssi
                current_location = calculate_current_location(latest_rssi_data)
                print(f"Data from [{location}] ({rssi} dBm) -> Current Location: {current_location}")
            
            except Exception as e:
                print(f"Error handling message: {e}")