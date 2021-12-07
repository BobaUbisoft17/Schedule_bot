import convertapi

async def convert(filename: str):
    convertapi.api_secret = 'CL1X36TPQhqkEVKa'
    convertapi.convert('csv', {
        'File': "schedule_bot/schedule_tables/" + filename,
        'Delimiter': 'semicolon',
    }, from_format = 'pdf').save_files("schedule_bot/schedule_tables/")
