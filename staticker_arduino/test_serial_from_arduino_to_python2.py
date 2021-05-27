from asyncio import get_event_loop
import asyncio
from serial_asyncio import open_serial_connection

class ArduinoAsyncSerial:
    def __init__(self):
        self.url = '/dev/ttyACM0'
        self.baudrate = 9600
        self.reader = None
        self.writer = None

    def start_listen(self):
        loop = get_event_loop()
        loop.create_task(self._listen())

    async def _listen(self):
        self.reader, self.writer = await open_serial_connection(
            url=self.url, baudrate=self.baudrate)
        while True:
            rawline = await self.reader.readline()
            try:
                line = str(rawline, 'utf-8')
                dic = self.decode(line)
            except:
                dic = None
            if dic:
                await self._exec_read_process(dic)

    async def _write(self, string):
        try:
            b = string.encode() + b''
            self.writer.write(b)
        except Exception as e:
            raise e

    def register_read_process(self, callable):
        self.read_process = callable

    async def _exec_read_process(self, dic):
        self.read_process(dic)

    def decode(self, string):
        return {}

async def write_serial():
    while True:
        await asyncio.sleep(2)
        print("write")
        await ard._write("!")
        
ard = ArduinoAsyncSerial()
ard.register_read_process(print)
ard.start_listen()

mainloop = get_event_loop()
mainloop.create_task(write_serial())

try:
    mainloop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    mainloop.close()
