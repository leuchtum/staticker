import asyncio
from operator import pos
import serial.tools.list_ports
from serial_asyncio import open_serial_connection
import json
from .log import logger

BRIGHTNESS_INPUTDEV = 0.2
BRIGHTNESS_SCOREDEV = 0.5
OWNER_COLOR_INPUTDEV = [255, 0, 0]
GOAL_COLOR_INPUTDEV = [0, 255, 0]
OWNER_COLOR_SCOREDEV = [200, 255, 255]
GOAL_COLOR_SCOREDEV = [200, 255, 255]
ARRAYLEN = 10


def get_arduino_port():
    for cp in serial.tools.list_ports.comports():
        for _, val in cp.__dict__.items():
            if isinstance(val, str):
                if "arduino" in val.lower():
                    return cp.device


class ArduinoAsyncSerial:
    def __init__(self):
        self.url = get_arduino_port()
        self.baudrate = 115200
        self.reader = None
        self.writer = None
        self.available = False

    async def startup(self):
        try:
            await self._open_connection()
        except:
            self.available = False
            logger.debug("Serial connection not available.")
        else:
            asyncio.create_task(self._listen())
            self.available = True
            logger.debug("Serial connection is available.")

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

    async def set_leds(self, game):
        def make_message(led, history, bright, goal_color, owner_color):
            r = [0 for _ in range(ARRAYLEN)]
            g = [0 for _ in range(ARRAYLEN)]
            b = [0 for _ in range(ARRAYLEN)]
            for i, key in enumerate(history):
                if key == "g":
                    r[i] = int(goal_color[0] * bright)
                    g[i] = int(goal_color[1] * bright)
                    b[i] = int(goal_color[2] * bright)
                elif key == "o":
                    r[i] = int(owner_color[0] * bright)
                    g[i] = int(owner_color[1] * bright)
                    b[i] = int(owner_color[2] * bright)
                else:
                    raise ValueError
            return {"pos": led, "R": r, "G": g, "B": b}

        for key in ["wd", "wo", "bd", "bo"]:
            history = game.get_player_history(key)
            msg = make_message(
                key,
                history,
                BRIGHTNESS_INPUTDEV,
                GOAL_COLOR_INPUTDEV,
                OWNER_COLOR_INPUTDEV,
            )
            await self._write("setled", msg)
            await asyncio.sleep(0.03)

        ws = []
        bs = []
        for action in game.history.split("_"):
            if action[0] == "g":
                if action[1] == "w":
                    ws.append("g")
                else:
                    bs.append("g")
            else:
                if action[1] == "w":
                    bs.append("o")
                else:
                    ws.append("o")

        msg = make_message(
            "ws", ws, BRIGHTNESS_SCOREDEV, GOAL_COLOR_SCOREDEV, OWNER_COLOR_SCOREDEV
        )
        await self._write("setled", msg)
        await asyncio.sleep(0.03)

        msg = make_message(
            "bs", bs, BRIGHTNESS_SCOREDEV, GOAL_COLOR_SCOREDEV, OWNER_COLOR_SCOREDEV
        )
        await self._write("setled", msg)
        await asyncio.sleep(0.03)

    async def clear_leds(self):
        await self._write("clear", "all")


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
