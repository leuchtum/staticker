import asyncio
import serial

s = serial.Serial('/dev/ttyACM0', 9600)


def test_serial():
    print("start print")
    loop.call_soon(s.write, "ok\n".encode())
    print("end print")
    
    print("start read")
    text = ""
    msg = s.read().decode()
    while (msg != '\n'):
        text += msg
        msg = s.read().decode()
    print(text)
    print("end read")
    

loop = asyncio.get_event_loop()
loop.add_reader(s, test_serial)
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    loop.close()
