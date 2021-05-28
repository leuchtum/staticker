import asyncio
from serial_asyncio import open_serial_connection
import json


class ArduinoAsyncSerial:
    def __init__(self):
        self.url = '/dev/ttyACM0'
        self.baudrate = 115200
        self.reader = None
        self.writer = None

    async def start_listen(self):
        await self._open_connection()
        asyncio.create_task(self._listen())

    async def _open_connection(self):
        self.reader, self.writer = await open_serial_connection(
            url=self.url, baudrate=self.baudrate)

    async def _listen(self):
        while True:
            rawline = await self.reader.readline()
            try:
                line = str(rawline, 'utf-8')
                dic = json.loads(line)
            except:
                dic = None
            if dic:
                self._exec_read_process(dic)

    async def _write(self, dic):
        raw = (str(json.dumps(dic)) + "\n").encode()
        try:
            self.writer.write(raw)
        except Exception as e:
            raise e # TODO 

    def register_read_process(self, callable):
        self.read_process = callable

    def _exec_read_process(self, dic):
        self.read_process(dic)


if __name__ == "__main__":
    
    async def main():
        await ard.start_listen()

    async def write():
        while True:
            print("write")
            await asyncio.sleep(0.5)
            a = dict(mode="setLED")
            await ard._write(a)
        
    ard = ArduinoAsyncSerial()
    ard.register_read_process(print)
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.create_task(write())
    loop.run_forever()
