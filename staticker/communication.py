import asyncio
from serial_asyncio import open_serial_connection
import json
from .log import logger

RED = [255, 0, 0]
GREEN = [0, 255, 0]
BLUE = [0, 0, 255]
ARRAYLEN = 10


class ArduinoAsyncSerial:
    def __init__(self):
        self.url = "/dev/ttyACM0"
        self.baudrate = 115200
        self.reader = None
        self.writer = None
        self.available = False

    async def startup(self):
        try:
            await self._open_connection()
        except:
            self.available = False
        else:
            asyncio.create_task(self._listen())
            self.available = True
            logger.debug("Serial connection opened.")

    async def _open_connection(self):
        self.reader, self.writer = await open_serial_connection(
            url=self.url, baudrate=self.baudrate
        )

    async def _listen(self):
        try:
            while True:
                rawline = await self.reader.readline()
                try:
                    line = str(rawline, "utf-8")
                    dic = json.loads(line)
                except:
                    logger.warning("Received unreadable JSON.")
                else:
                    asyncio.create_task(self._decode(dic))
                    logger.debug(f"Received package {dic}.")

        except Exception as e:  # TODO
            self.available = False

    async def _write(self, mode, msg):
        package = {"mode": mode, "msg": msg}
        raw = (str(json.dumps(package)) + "\n").encode()

        try:
            self.writer.write(raw)
        except Exception as e:
            raise e  # TODO
        else:
            logger.debug(f"Sent package {package}.")

    def set_button_callback(self, callable):
        self._button_callback = callable

    async def _decode(self, dic):
        mode = dic["mode"]
        msg = dic["msg"]

        if mode == "pressed":
            logger.debug(f"Decoded as button press at position {msg}.")
            await self._button_callback(msg)
        elif mode == "echo":
            logger.debug(f"Decoded as echo with message {msg}.")
        elif mode == "error":
            raise Exception(f"Error from Arduino: {msg}")

    async def set_leds(self, position, player_history):
        leds = [[0, 0, 0] for _ in range(ARRAYLEN)]
        for i in range(len(player_history)):
            if player_history[i] == "g":
                leds[i] = GREEN
            elif player_history[i] == "o":
                leds[i] = RED
            else:
                raise ValueError
        msg = {"position": position, "leds": leds}
        await self._write("setled", msg)


arduino = ArduinoAsyncSerial()

if __name__ == "__main__":

    async def main():
        await arduino.startup()

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
