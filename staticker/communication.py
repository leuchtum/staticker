import asyncio
from serial_asyncio import open_serial_connection
import json


class ArduinoAsyncSerial:
    def __init__(self):
        self.url = '/dev/ttyACM0'
        self.baudrate = 115200
        self.reader = None
        self.writer = None
        self.available = False

    async def start_listen(self):
        try:
            await self._open_connection()
        except:
            self.available = False
        else:
            asyncio.create_task(self._listen())
            self.available = True

    async def _open_connection(self):
        self.reader, self.writer = await open_serial_connection(
            url=self.url, baudrate=self.baudrate)

    async def _listen(self):
        try:
            while True:
                rawline = await self.reader.readline()
                try:
                    line = str(rawline, 'utf-8')
                    dic = json.loads(line)
                except:
                    dic = None
                if dic:
                    self.callable(dic)
        except Exception as e: #TODO
            self.available = False
            
    async def _write(self, dic):
        if type(dic) != dict:
            raise ValueError
        
        raw = (str(json.dumps(dic)) + "\n").encode()
        try:
            self.writer.write(raw)
        except Exception as e:
            raise e # TODO 

    def set_callback(self, callable):
        self.callable = callable


arduino = ArduinoAsyncSerial()

if __name__ == "__main__":
    
    async def main():
        await arduino.start_listen()

    async def write():
        while True:
            print("write")
            await asyncio.sleep(0.5)
            a = dict(mode="setLED")
            await arduino._write(a)
        
    arduino.register_read_process(print)
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.create_task(write())
    loop.run_forever()
