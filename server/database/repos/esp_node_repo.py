from psycopg.rows import class_row
from psycopg_pool import AsyncConnectionPool

from models.esp_node import EspNode

class EspNodeRepo:
    def __init__(self, connection_pool: AsyncConnectionPool) -> None:
        self._connection_pool = connection_pool

    async def insert_esp_node(self,esp_node: EspNode):
        """Insert a new esp-node into the database."""

        async with self._connection_pool.connection() as conn:
            await conn.execute(
                """
                INSERT INTO esp_nodes (name, room_name)
                VALUES (%s, %s, %s, %s)
                """,
                (esp_node.name, esp_node.room_name),
            )

    async def get_all(self) -> list[EspNode]:
        async with self._connection_pool.connection() as conn:
            async with conn.cursor(row_factory=class_row(EspNode)) as cur:
                await cur.execute(
                    """
                    SELECT *
                    FROM esp_nodes
                    """
                )
                result = await cur.fetchall()

                if len(result) == 0:
                    raise ValueError("No esp-nodes found")
                return result