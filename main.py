import asyncio

from bot import bot
from http_requests import check_content
from pathlib import Path


async def main():
    await asyncio.gather(
        bot.polling(),
        check_content()
    )


if __name__ == "__main__":
    Path("./files").mkdir(parents=True, exist_ok=True)
    asyncio.run(main())
