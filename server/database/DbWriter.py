import asyncio

from database.repos.detection_repo import DetectionRepo
from models.detection import Detection


class DbWriter:

    def __init__(self,
        message_queue: asyncio.Queue,
        detection_repo: DetectionRepo,
    ) -> None:
        self.message_queue = message_queue
        self.detection_repo = detection_repo

    async def run(self):
        while True:
            message = await self.message_queue.get()
            try:
                await self.write(message)
            finally:
                self.message_queue.task_done()


    async def write(self, message):
        match message:
            case Detection():
                await self.detection_repo.insert_detection(message)

            case "XYT":
                pass

            case _:
                raise TypeError(
                    f"Unsupported message type {type(message).__name__}"
                )





