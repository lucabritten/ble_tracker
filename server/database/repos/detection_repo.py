from psycopg_pool import AsyncConnectionPool

from models.detection import Detection

class DetectionRepo:

    def __init__(
        self,
        connection_pool: AsyncConnectionPool,
    ) -> None:
        self._connection_pool = connection_pool

    async def insert_detection(
            self,
            detection: Detection
    ) -> None:
        """Store a Bluetooth detection of the tracked device."""

        async with self._connection_pool.connection() as conn:
            await conn.execute(
                """
                INSERT INTO detection (device_name, esp_node_name, rssi, arrival_time)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    detection.device_name,
                    detection.esp_node_name,
                    detection.rssi,
                    detection.arrival_time
                ),
            )