from psycopg2.pool import ThreadedConnectionPool

from models.localisation import Localisation

class LocalisationRepo:
    def __init__(self, connection_pool: ThreadedConnectionPool) -> None:
        self._connection_pool = connection_pool

    def insert_localisation(self, localisation: Localisation) -> None:
        """Store a calculated localisation of a device."""
        conn = self._connection_pool.getconn()

        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO localisation (device_id, x, y, est_location)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (localisation.device_id, localisation.x, localisation.y, localisation.estimated_location)
                    )
        finally:
            self._connection_pool.putconn(conn)