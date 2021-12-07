import sqlite3


def add_id(peer_id):
    db = sqlite3.connect("users_id.db")
    cursor = db.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS users_id (
        id INTEGER
    )"""
    )
    db.commit()
    cursor.execute("SELECT * FROM users_id WHERE id=?", [peer_id])
    if cursor.fetchone() is None:
        cursor.execute(
            "INSERT INTO users_id (id) VALUES(?)", [peer_id]
        )
        db.commit()
        """cursor.close()
        db.close()
        return False"""
    """else:
        cursor.close()
        db.close()
        return True"""
    cursor.close()
    db.close()


def del_id(peer_id):
    db = sqlite3.connect("users_id.db")
    cursor = db.cursor()

    cursor.execute("SELECT * FROM users_id WHERE id=?", [peer_id])
    if cursor.fetchone() is None:
        return "Вы не подписаны на рассылку"
    else:
        cursor.execute("DELETE FROM users_id WHERE id=?", [peer_id])
        db.commit()

    cursor.close()
    db.close()


def get_id():
    db = sqlite3.connect("users_id.db")
    cursor = db.cursor()

    users_id = [value[0] for value in cursor.execute("SELECT id FROM users_id")]
    
    cursor.close()
    db.close()
    return users_id


"""def check_id(peer_id):
    db = sqlite3.connect("users_id.db")
    cursor = db.cursor()"""
