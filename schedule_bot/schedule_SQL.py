"Mодуль для записи распиания в SQL таблицу"
import sqlite3
from convert_to_class import give_to_class


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
    for schedule in give_to_class():
        cursor.execute(
            "INSERT INTO schedule (class, schedule) VALUES (?, ?)", (schedule.clas, schedule.schedule)
        )
    db.commit()
    cursor.close()
    connect.close()

init_db(True)
"""if __name__ == "__main__":
    init_db(True)"""
