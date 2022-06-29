"""Файл для работы с БД."""

import aiosqlite
import sqlite3


async def create_table():
    """Функция для создания БД."""
    async with aiosqlite.connect("db_users.db") as db:
        await db.execute(
            """CREATE TABLE IF NOT EXISTS users_db (
            id INTEGER,
            school TEXT,
            class TEXT,
            newsletter TEXT
        )"""
        )
        await db.commit()


async def add_id(user_id):
    """Функция для добавления пользователя в БД

    Функция принимает в качестве аогумнта id пользователя
    и записывает в БД, оставляя остальные ячейки пустыми
    """
    async with aiosqlite.connect("db_users.db") as db:
        async with db.execute("SELECT * FROM users_db WHERE id=?", [user_id]) as cursor:
            if await cursor.fetchone() is None:
                await db.execute(
                    "INSERT INTO users_db (id, school, class, newsletter) VALUES(?, ?, ?, ?)",
                    [user_id, "", "", ""],
                )
                await db.commit()


async def subscribe_on_newsletter(user_id, school):
    """Функция для подписки на рассылку.

    Функция принимает в качетсве аргумента id пользователя
    и его школы. Если пользователя нет в БД, то функция записывает
    его и его школу, иначе меняет значение в ячейке 'newsletter'
    """
    async with aiosqlite.connect("db_users.db") as db:
        async with db.execute("SELECT * FROM users_db WHERE id=?", [user_id]) as cursor:
            if await cursor.fetchone() is None:
                await db.execute(
                    "INSERT INTO users_db (id, school, class, newsletter) VALUES(?, ?, ?, ?)",
                    [user_id, "", "", school],
                )
                await db.commit()
            else:
                await db.execute(
                    f"UPDATE users_db SET newsletter='{school}' WHERE id='{user_id}'"
                )
                await db.commit()


async def unsubscribe_on_newsletter(user_id):
    """Функция для отписки от рассылки.

    Функция принимает в качетсве аргумента id пользователя и
    удаляет данные из ячейки 'newsletter'
    """
    async with aiosqlite.connect("db_users.db") as db:
        await db.execute(f"UPDATE users_db SET newsletter='' WHERE id='{user_id}'")
        await db.commit()


async def change_user_class(user_id, school="", class_=""):
    """Функция запоминания класса, изменения и удаления класса.

    Функция в качестве аргумента принимает id, школу и класс пользователя,
    после чего записывает/изменяет/удаляет эти данные.
    """
    async with aiosqlite.connect("db_users.db") as db:
        async with db.execute("SELECT * FROM users_db WHERE id=?", [user_id]) as cursor:
            if await cursor.fetchone() is None:
                await db.execute(
                    "INSERT INTO users_db (id, school, class, newsletter) VALUES(?, ?, ?, ?)",
                    [user_id, school, class_, ""],
                )
                await db.commit()
            else:
                await db.execute(
                    f"UPDATE users_db SET class='{class_}', school='{school}' WHERE id='{user_id}'"
                )
                await db.commit()


async def check_school_and_class(user_id, pld_school):
    """Функция для проверки класса и школы пользователя.

    Вызывается при отправления расписания по кнопке 'Узнать расписание' если в БД есть класс пользователя.
    Проверяет значение школы со значением школы в payload, если совпадает, то возвращает True, иначе False.
    """
    async with aiosqlite.connect("db_users.db") as db:
        async with db.execute("SELECT * FROM users_db WHERE id=?", [user_id]) as cursor:
            if await cursor.fetchone() is None:
                return False
            else:
                async with db.execute("SELECT * FROM users_db WHERE id=?", [user_id]) as user_data:
                    school, class_ = (await user_data.fetchone())[1:3]
                    if class_ != "" and pld_school == school:
                        return True
                    else:
                        return False


async def check_class(user_id):
    """Функция для проверки наличия данных о классе пользователя в БД.

    Проверяет есть ли информация о классе пользователя и возвращает булевое значение в зависимости.
    """
    async with aiosqlite.connect("db_users.db") as db:
        async with db.execute("SELECT class FROM users_db WHERE id=?", [user_id]) as cursor:
            if await cursor.fetchone() is None:
                return False
            else:
                async with db.execute("SELECT class FROM users_db WHERE id=?", [user_id]) as user_data:
                    if (await user_data.fetchone())[0] != "":
                        return True
                    else:
                        return False


async def get_school_and_class(user_id):
    """Функция для получения класса пользователя."""
    async with aiosqlite.connect("db_users.db") as db:
        async with db.execute("SELECT * FROM users_db WHERE id=?", [user_id]) as cursor:
            info = await cursor.fetchone()
            school, class_ = info[1:3]
            return school, class_


async def check_user_subscription(user_id):
    """Функция для проверки подписки пользователя на уведомления."""
    async with aiosqlite.connect("db_users.db") as db:
        async with db.execute("SELECT newsletter FROM users_db WHERE id=?", [user_id]) as cursor:
            if (await cursor.fetchone())[0] == "":
                return False
            else:
                return True


async def get_users_id(school):
    """Функция для получения всех id-пользователей для уведомления о новом/обновлённом расписании."""
    async with aiosqlite.connect("db_users.db") as db:
        async with db.execute("SELECT id FROM users_db WHERE newsletter=?", [school]) as cursor:
            users_id = [value[0] for value in await cursor.fetchall()]
            return users_id
