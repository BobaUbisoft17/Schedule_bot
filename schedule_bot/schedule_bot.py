import convertapi

def convert(filename):
    convertapi.api_secret = 'CL1X36TPQhqkEVKa'
    convertapi.convert('csv', {
        'File': 'C:/Users/Udich/schedule_bot/csv_schedule/' + filename,
        'Delimiter': 'semicolon',
    }, from_format = 'pdf').save_files('C:/Users/Udich/schedule_bot/csv_schedule/')
