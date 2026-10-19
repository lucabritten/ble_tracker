from psycopg2.pool import ThreadedConnectionPool

from models.device import Device
from shared.utility import is_irk_address


class DeviceRepo:
    def __init__(self, connection_pool: ThreadedConnectionPool) -> None:
        self._connection_pool = connection_pool

    def insert_device(self, device: Device) -> None:
        """Insert a tracked device into the database."""
        conn = self._connection_pool.getconn()

        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO devices (name, display_name, irk)
                        VALUES (%s, %s)
                        """,
                        (device.name, device.display_name, device.irk),
                    )
        finally:
            self._connection_pool.putconn(conn)

    def get_device_by_irk(self, irk: str) -> int:
        if not is_irk_address(irk):
            raise ValueError(f"Invalid irk address: {irk}")

        conn = self._connection_pool.getconn()

        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """       
                        SELECT id
                        FROM devices
                        WHERE irk = %s
                        """,
                        irk
                    )
                    result = cur.fetchone()
                    if result is None:
                        raise ValueError(f"Device with {irk} not found")
                    return result[0]
        finally:
            self._connection_pool.putconn(conn)
