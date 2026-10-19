import json
import asyncio
import aiomqtt
import time

from models.detection import Detection
from services.tracking_service import TrackingService


class MQTTIngestor:

    def __init__(
            self,
            broker_ip,
            username,
            password,
            topic,
            message_queue: asyncio.Queue,
            tracking: TrackingService
    ):
        self.broker_ip = broker_ip
        self.username = username
        self.password = password
        self.topic = topic
        self.message_queue = message_queue
        self.tracking = tracking

    async def listen(self):
        while True:
            try:
                async with aiomqtt.Client(
                    hostname=self.broker_ip,
                    username=self.username,
                    password=self.password) as client:

                    await client.subscribe(self.topic)

                    async for message in client.messages:
                        arrival_time = time.time() # Add field to detection
                        try:
                            payload = json.loads(message.payload.decode("utf-8"))

                            if self.is_valid(payload):
                                detection = self.to_detection(payload, arrival_time)
                                await self.message_queue.put(detection)
                                self.tracking.on_detection(detection)

                        except (UnicodeDecodeError, json.JSONDecodeError) as e:
                            print(f"Error decoding payload: {e}")
            except aiomqtt.MqttError as e:
                print(f"MQTT connection error: {e}. Retrying in 5 seconds...")
                await asyncio.sleep(5)


    @staticmethod
    def is_valid(payload) -> bool:
        """Validates whether the payload is in the following format:
            {
                "device_name": <device name>,
                "esp_name": <esp name>,
                "rssi": <rssi>
            }
        """
        if not isinstance(payload, dict):
            return False

        return (
                "device_name" in payload
                and "esp_name" in payload
                and "rssi" in payload
                and type(payload["rssi"]) is int
        )


    @staticmethod
    def to_detection(payload, arrival_time: float) -> Detection:
        """Converts payload to a detection object"""
        return Detection(
            device_name=payload["device_name"],
            esp_node_name=payload["esp_name"],
            rssi=payload["rssi"],
            arrival_time=arrival_time
        )