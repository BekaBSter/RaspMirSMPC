import asyncio

from bot import bot
from http_requests import check_content
from pathlib import Path

from Settings import out


async def main():
    await asyncio.gather(
        bot.polling(none_stop=True, request_timeout=300),
        check_content()
    )


if __name__ == "__main__":
    Path("./files").mkdir(parents=True, exist_ok=True)
    try:
        asyncio.run(main())
    except KeyboardInterrupt as e:
        out("Остановка бота", "r")
