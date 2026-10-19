from psycopg2.pool import ThreadedConnectionPool

from models.esp_node import EspNode

class EspNodeRepo:
    def __init__(self, connection_pool: ThreadedConnectionPool):
        self._connection_pool = connection_pool

    def insert_esp_node(self,esp_node: EspNode):
        """Insert a new esp-node into the database."""
        conn = self._connection_pool.getconn()

        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO esp_nodes (name, room_name)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (esp_node.name, esp_node.room_name),
                    )
        finally:
            self._connection_pool.putconn(conn)