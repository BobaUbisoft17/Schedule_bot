import convertapi

def convert(filename: str):
    convertapi.api_secret = 'CL1X36TPQhqkEVKa'
    convertapi.convert('csv', {
        'File': filename,
        'Delimiter': 'semicolon',
    }, from_format = 'pdf').save_files()
