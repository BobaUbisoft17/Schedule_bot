import sqlite3


def get_schedule(clas: str) -> str:
    db = sqlite3.connect("schedule.db")
    cursor = db.cursor()
    schedules = []
    if len(list(cursor.execute(f"SELECT * FROM schedule WHERE class = '{clas}'"))) == 1:
        return list(cursor.execute(f"SELECT * FROM schedule WHERE class = '{clas}'"))[0][1]
    elif len(list(cursor.execute(f"SELECT * FROM schedule WHERE class = '{clas}'"))) > 1:
        for schedule in cursor.execute(f"SELECT * FROM schedule WHERE class = '{clas}'"):
            schedules.append('\n'.join(schedule))
        return '================\n'.join(schedules)
    else:
        return "Расписание для данного класса не найдено"
