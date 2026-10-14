import asyncio
from mqtt_listener import start_mqtt_listener

if __name__ == "__main__":
    try:
        asyncio.run(start_mqtt_listener())
    except KeyboardInterrupt:
        print("Server stopped by user.")