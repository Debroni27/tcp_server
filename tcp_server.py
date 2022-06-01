# Server side

import logging
import re
import pendulum
import asyncio

counter = 0

"""
# BBBB - номер участника
# NN - id канала
# HH - часы
# MM - минуты
# SS - секунды
# ZHQ - десятые сотые тысячные секунд
# GG - номер группы
# x - пробельный символ

# Формат поступаемых данных BBBBxNNxHHx:MM:SS.zhqxGG
"""

# Создаем логгирование для работы нашего сервера
logging.basicConfig(filename="server.log", level=logging.INFO)
logger = logging.getLogger("server")
logger.setLevel(logging.INFO)


# tcp сервер для обработки данных
async def run_server(host, port):
    server = await asyncio.start_server(serve_client, host, port)
    # Уведомление о запуске
    print("*" * 50)
    print("Server started on {}:{}".format(host, port))
    print("*" * 50)
    logger.info("Server started successful")
    await server.serve_forever()


# Логика обработки данных
async def serve_client(reader, writer):
    global counter
    cid = counter
    counter += 1
    print(f'Client #{cid} connected')
    logger.info(f'Client #{cid} connected')

    data = await reader.read(100)
    serializer = data.decode()

    body = re.search(r"^(\d\d\d\d) ([a-zA-z0-9]{2}) (\d\d:\d\d:\d\d\.\d\d\d) (\d\d)\s?$", serializer)

    if body:
        record = pendulum.parse(body.group(3))
        response = "Спортсмен, нагрудный номер {} прошел отсечку {} в <<{}>>\n".format(body.group(1), body.group(2), record.format("h:m:s.ms"))
        with open("records.log", "a", newline="") as f:
            f.write(response)
            f.close()
        logger.info("The data were accepted and processed ")
        if body.group(4) == "00":
            print(response)
            writer.write(response.encode())
            await writer.drain()
        print("Work done!")
        writer.close()
        print(f'Client #{cid} has been served')
        logger.info("Connection closed")
        logger.info("-" * 50)

    else:
        logger.error("!!!Data validation error!!!")
        print("!!!Data validation error!!")
        writer.close()
        print(f'Client #{cid} has been served')
        logger.info("Connection closed with validate error")
        logger.info("-"*50)


if __name__ == '__main__':
  asyncio.run(run_server('127.0.0.1', 9000))