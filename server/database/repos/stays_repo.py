from psycopg_pool import AsyncConnectionPool

from models.stay_event import StayEvent


class StaysRepo:

    def __init__(self,
                 connection_pool: AsyncConnectionPool
                 ) -> None:
        self._connection_pool = connection_pool

    async def insert_stay_event(self, stay_event: StayEvent) -> None:
        async with self._connection_pool.connection() as conn:
            await conn.execute(
                """
                INSERT INTO stays (device_name, room_name, started_at)
                VALUES (%s, %s, to_timestamp(%s))
                """,
                (
                    stay_event.device_name,
                    stay_event.room,
                    stay_event.at
                )
            )

    async def update_stay_event(self, stay_event: StayEvent) -> None:
        async with self._connection_pool.connection() as conn:
            cur = await conn.execute(
                """
                UPDATE stays
                SET ended_at = to_timestamp(%s)
                WHERE device_name = %s AND ended_at IS NULL
                """,
                (
                    stay_event.at,
                    stay_event.device_name
                )
            )
            if cur.rowcount == 0:
                print(f"Kein aktiver Eintrag (ended_at IS NULL) für Gerät '{stay_event.device_name}' gefunden.")

    async def delete_open_stays(self):
        async with self._connection_pool.connection() as conn:
            await conn.execute(
                """
                DELETE FROM stays
                WHERE ended_at IS NULL
                """
            )
