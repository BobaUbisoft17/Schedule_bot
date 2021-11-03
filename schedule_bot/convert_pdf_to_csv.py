import convertapi

def convert(filename: str):
    convertapi.api_secret = 'CL1X36TPQhqkEVKa'
    convertapi.convert('csv', {
        'File': "schedule_bot/" + filename,
        'Delimiter': 'semicolon',
    }, from_format = 'pdf').save_files("schedule_bot")
