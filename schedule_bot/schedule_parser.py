import asyncio
from schedule_parser14 import parse


parsers = [parse]
async def schedule_parser(bot):
    while True:
        for parser in parsers:
            await parser(bot)
