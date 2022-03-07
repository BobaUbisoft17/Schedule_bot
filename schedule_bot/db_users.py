import sqlite3


def create_table():
    db = sqlite3.connect("db_users.db")
    cursor = db.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS users_db (
        id INTEGER,
        school TEXT,
        class TEXT,
        newsletter TEXT
    )"""
    )
    db.commit()
    cursor.close()
    db.close()


async def add_id(user_id):
    """Функция для добавления пользователя в БД
    
       Функция принимает в качестве аогумнта id пользователя
       и записывает в БД, оставляя остальные ячейки пустыми
    """
    db = sqlite3.connect("db_users.db")
    cursor = db.cursor()

    cursor.execute("SELECT * FROM users_db WHERE id=?", [user_id])
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO users_db (id, school, class, newsletter) VALUES(?, ?, ?, ?)", [user_id, "", "", ""])
        db.commit()
    cursor.close()
    db.close()


async def subscribe_on_newsletter(user_id, school):
    """Функция для подписки на рассылку.
       
       Функция принимает в качетсве аргумента id пользователя
       и его школы. Если пользователя нет в БД, то функция записывает
       его и его школу, иначе меняет значение в ячейке 'newsletter'
    """
    db = sqlite3.connect("db_users.db")
    cursor = db.cursor()

    cursor.execute("SELECT * FROM users_db WHERE id=?", [user_id])
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO users_db (id, school, class, newsletter) VALUES(?, ?, ?, ?)", [user_id, "", "", school])
        db.commit()
    else:
        cursor.execute(f"UPDATE users_db SET newsletter='{school}' WHERE id='{user_id}'")
        db.commit()
    cursor.close()
    db.close()


async def unsubscribe_on_newsletter(user_id):
    """Функция для отписки от рассылки.
       
       Функция принимает в качетсве аргумента id пользователя и
       удаляет данные из ячейки 'newsletter'
    """
    db = sqlite3.connect("db_users.db")
    cursor = db.cursor()

    cursor.execute(f"UPDATE users_db SET newsletter='' WHERE id='{user_id}'")
    db.commit()
    cursor.close()
    db.close()


async def change_user_class(user_id, school="", class_=""):
    """Функция запоминания класса, изменения и удаления класса.
    
       Функция в качестве аргумента принимает id, школу и класс пользователя,
       после чего записывает/изменяет/удаляет эти данные.
    """
    db = sqlite3.connect("db_users.db")
    cursor = db.cursor()

    cursor.execute("SELECT * FROM users_db WHERE id=?", [user_id])
    if cursor.fetchone() is None:
        cursor.execute("SELECT INTO users_db (id, school, class, newsletter) VALUES(?, ?, ?, ?)", [user_id, school, class_, ""])
        db.commit()
    else:
        cursor.execute(f"UPDATE users_db SET class='{class_}', school='{school}' WHERE id='{user_id}'")
        db.commit()
    cursor.close()
    db.close()


async def check_school_and_class(user_id, pld_school):
    db = sqlite3.connect("db_users.db")
    cursor = db.cursor()

    cursor.execute("SELECT * FROM users_db WHERE id=?", [user_id])
    if cursor.fetchone() is None:
        cursor.close()
        db.close()
        return False
    else:
        school, class_ = list(cursor.execute("SELECT * FROM users_db WHERE id=?", [user_id]))[0][1:3]
        if class_ != "" and pld_school == school:
            cursor.close()
            db.close()
            return True
        else:
            cursor.close()
            db.close()
            return False


async def check_class(user_id):
    db = sqlite3.connect("db_users.db")
    cursor = db.cursor()

    cursor.execute("SELECT class FROM users_db WHERE id=?", [user_id])
    if cursor.fetchone() is None:
        cursor.close()
        db.close()
        return False
    else:
        if list(cursor.execute("SELECT class FROM users_db WHERE id=?", [user_id]))[0][0] != "":
            cursor.close()
            db.close()
            return True
        else:
            cursor.close()
            db.close()
            return False



async def get_school_and_class(user_id):
    """Функция для получения класса пользователя.
    
       """
    db = sqlite3.connect("db_users.db")
    cursor = db.cursor()

    info = list(cursor.execute("SELECT * FROM users_db WHERE id=?", [user_id]))
    class_ = info[0][2]
    school = info[0][1]
    cursor.close()
    db.close()
    return school, class_


async def check_user_subscription(user_id):
    db = sqlite3.connect("db_users.db")
    cursor = db.cursor()

    if list(cursor.execute("SELECT newsletter FROM users_db WHERE id=?", [user_id]))[0][0] == "":
        cursor.close()
        db.close()
        return False
    else:
        cursor.close()
        db.close()
        return True


async def get_users_id(school):
    db = sqlite3.connect("db_users.db")
    cursor = db.cursor()

    users_id = [value[0] for value in cursor.execute("SELECT id FROM users_db WHERE newsletter=?", [school])]
    cursor.close()
    db.close()
    return users_id
