import asyncio
from threading import Timer

async def speak_async():
    print('OMG asynchronicity!')

def hello():
    print('hello')

def test():
    t = Timer(5, hello)
    print('timer')
    t.start()

# loop = asyncio.get_event_loop()
# loop.run_until_complete(speak_async())
# loop.close()
test()
print('no')