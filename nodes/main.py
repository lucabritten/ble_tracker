from mqtt_client import *
import time
import asyncio
import json

from shared.utility import load_from_json
from track_phone import get_rssi_for_device

CONFIG_FILE = "config/config.json"

def main():
    try:
        client = connect()
    except OSError as e:
        client = reconnect()
        
    while True:
        try:
            rssi = asyncio.run(get_rssi_for_device())
            if rssi is not None:
                esp_name = load_from_json(CONFIG_FILE, "mqtt", "device")
                device_name = load_from_json(CONFIG_FILE, "tracked_device", "name")
                payload = json.dumps({"device_name": device_name,"esp_name":esp_name, "rssi": rssi, "timestamp": time.time()})
                client.publish(topic, payload, qos=0)
                print(f"Gesendet: RSSI {rssi}")
        except Exception as e:
            print(f"Fehler beim Senden/Scannen: {e}")
            try:
                client = reconnect()
            except Exception:
                pass
                
        time.sleep(3)

if __name__ == "__main__":
    main()