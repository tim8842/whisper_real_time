import asyncio
import time

async def first():
    while True:
        for i in range(5):
            print("first")
            time.sleep(2) 
        await asyncio.sleep(10)

async def second():
    while True:
        time.sleep(1) 
        print("second")
        await asyncio.sleep(10)

async def main():
    task1 = asyncio.create_task(first())
    task2 = asyncio.create_task(second())

    await asyncio.gather(task1, task2)

asyncio.run(main())