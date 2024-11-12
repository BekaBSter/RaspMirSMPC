import asyncio

from bot import bot
from http_requests import check_content


async def main():
    await asyncio.gather(
        bot.polling(),
        check_content()
    )


if __name__ == "__main__":
    asyncio.run(main())
