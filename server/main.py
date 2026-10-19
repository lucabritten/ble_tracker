

async def main():
    pool = create_connection_pool(...)
    registry = Registry.load(...)                  # Schritt 2
    queue = asyncio.Queue()
    tracking = TrackingService(registry, queue)
    ingestor = MqttIngestor(..., queue=queue, registry=registry, tracking=tracking)
    writer = DbWriter(queue, ...)
    ticker = Ticker(tracking, interval=1.0)

    # estimator = RoomEstimator(room_of=registry.room_of)
    # tracking = TrackingService(registry.device_names(), estimator, emit=queue.put_nowait)

    async with asyncio.TaskGroup() as tg:
        tg.create_task(ingestor.listen())
        tg.create_task(writer.run())
        tg.create_task(ticker.run())