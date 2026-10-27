import asyncio

from database.repos.detection_repo import DetectionRepo
from database.repos.stays_repo import StaysRepo
from models.detection import Detection
from models.stay_event import StayEvent


class DbWriter:

    def __init__(self,
        message_queue: asyncio.Queue,
        detection_repo: DetectionRepo,
        stays_repo: StaysRepo
    ) -> None:
        self.message_queue = message_queue
        self.detection_repo = detection_repo
        self.stays_repo = stays_repo

    async def run(self):
        while True:
            message = await self.message_queue.get()
            try:
                await self.write(message)
            except Exception as e:
                print(f"Konnte {message} nicht schreiben: {e!r}")
            finally:
                self.message_queue.task_done()


    async def write(self, message):
        match message:
            case Detection():
                await self.detection_repo.insert_detection(message)

            case StayEvent():
                if message.kind == "started":
                    await self.stays_repo.insert_stay_event(message)
                else:
                    await self.stays_repo.update_stay_event(message)


            case _:
                raise TypeError(
                    f"Unsupported message type {type(message).__name__}"
                )





