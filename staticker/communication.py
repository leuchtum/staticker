from asyncio import get_event_loop
from serial_asyncio import open_serial_connection

'''
Spezification protocoll:

    Message composition:
        !X_M!
        
    !: Start and and characters
    X: Mode indentifier [0:9]
    _: Delimiter
    Start msg: !
    Mode
    End msg: !
    
'''

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

    def register_write_process(self, callable):
        self.write_process = callable

    async def _exec_read_process(self, dic):
        self.read_process(dic)

    def decode(self, string):
        if string.count("!") != 2:
            raise(Exception("Faulty message."))

        raw_msg = string.split("!")[1]
        msgs = raw_msg.split("_")
        dic = {}
        for msg in msgs:
            key = msg.split("=")[0]
            val = msg.split("=")[1]
            val = bool(int(val))
            dic[key] = val
        return dic
