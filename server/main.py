import asyncio

import psycopg
from psycopg_pool import AsyncConnectionPool

from database.repos.device_repo import DeviceRepo
from database.repos.esp_node_repo import EspNodeRepo
from database.repos.stays_repo import StaysRepo
from shared.utility import load_from_json
from database.registry import Registry
from database.DbWriter import DbWriter
from database.repos.detection_repo import DetectionRepo
from mqtt.mqttingestor import MQTTIngestor
from positioning.room_estimator import RoomEstimator
from services.tracking_service import TrackingService
from services.ticker import Ticker

CONFIG_FILE = "server/config/config.json"


async def main() -> None:
    mqtt_cfg = load_from_json(CONFIG_FILE, "mqtt")
    db_cfg = load_from_json(CONFIG_FILE, "postgres")

    dsn = psycopg.conninfo.make_conninfo(
        dbname=db_cfg["DB_NAME"],
        host=db_cfg["DB_HOST"],
        port=db_cfg["DB_PORT"],
        user=db_cfg["DB_USER"],
        password=db_cfg["DB_PASSWORD"]
    )

    async with AsyncConnectionPool(conninfo=dsn, open=False) as pool:

        # Setup
        devices = await DeviceRepo(pool).get_all()
        nodes = await EspNodeRepo(pool).get_all()
        stays = StaysRepo(pool)
        registry = Registry(devices, nodes)

        await stays.delete_open_stays()

        queue: asyncio.Queue = asyncio.Queue()
        estimator = RoomEstimator(node_rooms=registry.node_rooms)
        tracking = TrackingService(registry.device_names, estimator, emit=queue.put_nowait)

        # 5. Die drei Tasks
        ingestor = MQTTIngestor(
            mqtt_cfg["server_ip"],
            mqtt_cfg["user_name"],
            mqtt_cfg["user_pass"],
            "esp/tracking",
            message_queue=queue,
            tracking=tracking,
        )
        writer = DbWriter(queue, DetectionRepo(pool), stays)
        ticker = Ticker(tracking, interval=1.0)

        # 6. Starten und laufen lassen
        async with asyncio.TaskGroup() as tg:
            tg.create_task(ingestor.listen())
            tg.create_task(writer.run())
            tg.create_task(ticker.run())


if __name__ == "__main__":
    asyncio.run(main())