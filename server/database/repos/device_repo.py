from psycopg.rows import class_row
from psycopg_pool import AsyncConnectionPool

from models.device import Device
from shared.utility import is_irk_address


class DeviceRepo:
    def __init__(self, connection_pool: AsyncConnectionPool) -> None:
        self._connection_pool = connection_pool

    async def insert_device(self, device: Device) -> None:
        """Insert a tracked device into the database."""
        async with self._connection_pool.connection() as conn:
            await conn.execute(
                    """
                    INSERT INTO devices (name, display_name, irk)
                    VALUES (%s, %s, %s)
                    """,
                    (device.name, device.display_name, device.irk),
            )


    async def get_device_by_irk(self, irk: str) -> int:
        if not is_irk_address(irk):
            raise ValueError(f"Invalid irk address: {irk}")

        async with self._connection_pool.connection() as conn:
            async with conn.cursor(row_factory=class_row(Device)) as cur:
                await cur.execute(
                    """
                    SELECT id
                    FROM devices
                    WHERE irk = %s
                    """,
                    (
                        irk,
                    ),
                )

                result = await cur.fetchall()
                if not result or result is None:
                    raise ValueError(f"Invalid irk address: {irk}")

                return result[0].irk



    async def get_all(self) -> list[Device]:
        """Retrieve all devices."""
        async with self._connection_pool.connection() as conn:
            async with conn.cursor(row_factory=class_row(Device)) as cur:
                await cur.execute(
                    """
                    SELECT name, display_name, irk
                    FROM devices
                    """
                )
                results = await cur.fetchall()

                return results


