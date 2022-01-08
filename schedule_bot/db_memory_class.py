import sqlite3
import asyncio

def create_db():
    db = sqlite3.connect("memory_class.db")
    cursor = db.cursor()

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS memory_class (
        id INTEGER,
        class TEXT
    )"""
    )
    db.commit()
    cursor.close()
    db.close()


async def add_class_and_id(id, class_=None):
    db = sqlite3.connect("memory_class.db")
    cursor = db.cursor()
    if class_ == None:
        cursor.execute("SELECT * FROM memory_class WHERE id=?", [id])
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO memory_class (id, class) VALUES(?, ?)", [id, ""])
            db.commit()
    else:
        cursor.execute("SELECT * FROM memory_class WHERE id=?", [id])
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO memory_class (id, class) VALUES(?, ?)", [id, class_])
            db.commit()
        else:
            cursor.execute(f"Update memory_class SET class = '{class_}' WHERE id = '{id}'")
            db.commit()
    cursor.close()
    db.close()


async def check_class_id(id):
    db = sqlite3.connect("memory_class.db")
    cursor = db.cursor()
    
    cursor.execute("SELECT * FROM memory_class WHERE id=?", [id])
    if cursor.fetchone() is None:
        await add_class_and_id(id)
    if list(cursor.execute("SELECT class FROM memory_class WHERE id=?", [id]))[0][0] == "":
        cursor.close()
        db.close()
        return False
    else:
        cursor.close()
        db.close()
        return True


async def del_class_id(id):
    db = sqlite3.connect("memory_class.db")
    cursor = db.cursor()

    cursor.execute("SELECT * FROM memory_class WHERE id=?", [id])
    if cursor.fetchone() is None:
        cursor.close()
        db.close()
        return False
    else:
        cursor.execute("DELETE FROM memory_class WHERE id=?", [id])
        db.commit()
        cursor.close()
        db.close()
        return True


async def get_class_id(id):
    db = sqlite3.connect("memory_class.db")
    cursor = db.cursor()

    class_ = list(cursor.execute("SELECT class FROM memory_class WHERE id=?", [id]))[0][0]
    cursor.close()
    db.close()
    return class_
