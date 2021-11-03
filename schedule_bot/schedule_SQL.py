"Mодуль для записи распиания в SQL таблицу"
import sqlite3
from csv_parser import get_classes_schedules


def init_db(force: bool):
    db = sqlite3.connect("schedule.db")
    cursor = db.cursor()
    if force:
        cursor.execute("DROP TABLE IF EXISTS schedule")

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS schedule (
		class TEXT,
		schedule TEXT
	)"""
    )

    db.commit()
    for schedule in get_classes_schedules():
        cursor.execute(
            "INSERT INTO schedule (class, schedule) VALUES (?, ?)", (schedule.class_name, schedule.schedule)
        )
    db.commit()
    cursor.close()
    db.close()
