# from asyncio import get_event_loop
# from serial_asyncio import open_serial_connection


def decode(string):
    if string.count("!") == 2:
        raw_msg = string.split("!")[1]
        msgs = raw_msg.split("_")
        dic = dict()
        for msg in msgs:
            key = msg.split("=")[0]
            val = msg.split("=")[1]
            val = bool(int(val))
            dic[key] = val
        return dic
    else:
        raise (Exception("Faulty message."))


async def run():
    reader, writer = await open_serial_connection(url="/dev/ttyACM0", baudrate=9600)
    while True:
        rawline = await reader.readline()
        line = str(rawline, "utf-8")
        try:
            dic = decode(line)
        except:
            dic = None
        print(dic)


loop = get_event_loop()
loop.run_until_complete(run())
