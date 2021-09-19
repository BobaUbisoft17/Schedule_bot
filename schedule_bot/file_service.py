import sqlite3


def get_schedule(clas):
    db = sqlite3.connect("schedule.db")
    cursor = db.cursor()
    schedules = []
    if len(list(cursor.execute(f"SELECT * FROM schedule WHERE class = '{clas}'"))) == 1:
        return '\n'.join(list(cursor.execute(f"SELECT * FROM schedule WHERE class = '{clas}'"))[0])       
    elif len(list(cursor.execute(f"SELECT * FROM schedule WHERE class = '{clas}'"))) > 1:
        for schedule in cursor.execute(f"SELECT * FROM schedule WHERE class = '{clas}'"):
            schedules.append('\n'.join(schedule))
        return '================\n'.join(schedules)
    else:
        return "Расписание для данного класса не найдено"