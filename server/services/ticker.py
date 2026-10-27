import asyncio
import time
from services.tracking_service import TrackingService


class Ticker:

    def __init__(self, tracking: TrackingService, interval: float):
        self.tracking = tracking
        self.interval = interval

    async def run(self):
        while True:
            try:
                self.tracking.on_tick(time.time())
            except Exception as e:
                print(e)
            finally:
                await asyncio.sleep(self.interval)

