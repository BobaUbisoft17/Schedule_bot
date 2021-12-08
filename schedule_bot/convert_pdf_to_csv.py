import convertapi
from config import CONVERTAPITOKEN

async def convert(filename: str):
    convertapi.api_secret = CONVERTAPITOKEN
    convertapi.convert('csv', {
        'File': "schedule_bot/schedule_tables/" + filename,
        'Delimiter': 'semicolon',
    }, from_format = 'pdf').save_files("schedule_bot/schedule_tables/")
