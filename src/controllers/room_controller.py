from binascii import a2b_base64
from db.database import Database
import os
import sys
import sqlite3
sys.path.append(os.path.abspath(os.path.join('..', 'backend')))


def delete(id, ):
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    cursor.execute("DELETE FROM Room WHERE id=?", (id,))
    connexion.commit()


def update(name, type, date_creation, description,  reservation_id):
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    sql_query = "UPDATE Room " \
        "SET name=?, type=?, race=?, age=?, " \
        "date_creation=?, description=?, =? " \
        "WHERE reservation_id=?"
    cursor.execute(sql_query, (name, type, date_creation,
                               description,  reservation_id,))
    connexion.commit()
    return cursor.fetchone()


def insert(name, type, date_creation, description,  reservation_id):
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    cursor.execute(
        "INSERT INTO Room(name, type, date_creation, "
        "description,  reservation_id) "
        "VALUES(?, ?, ?, ?, ?,?,?, ?)",
        (name, type, date_creation, description,  reservation_id,))
    connexion.commit()


def select_by_id(id):
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    sql = "SELECT * FROM Room s WHERE s.id == ? "
    cursor.execute((sql), (id,))
    return cursor.fetchone()


def select_five_random_Room():
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    cursor.execute('SELECT * FROM Room ORDER BY random() LIMIT 5')
    return cursor.fetchall()


def order_by_date_creation(option):
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    cursor.execute(" SELECT * FROM Room WHERE "
                   "strftime('%Y-%m-%d','now') >= strftime"
                   "('%Y-%m-%d',date_creation) ORDER BY "
                   "date_creation DESC")
    if option == 1:
        return get_db().Room_to_list_of_dict(cursor.fetchall())
    else:
        return cursor.fetchmany(5)


def select_by_type(type):
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    sql = "SELECT * FROM Room s WHERE s.type == ? "
    cursor.execute((sql), (type,))
    return cursor.fetchall()


def select_all():
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    cursor.execute('SELECT * FROM Room')
    return cursor.fetchall()


def select_by_name(name):
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    sql_query = "%" + name + "%"
    cursor.execute("SELECT * FROM Room WHERE name LIKE ?", (sql_query,))
    return cursor.fetchone()


def select_by_reservation_id(reservation_id):
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    cursor.execute("SELECT * FROM Room WHERE reservation_id = ?",
                   (reservation_id,))
    return cursor.fetchall()


def select__by_reservation_id(reservation_id):
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    cursor.execute("SELECT  FROM Room WHERE reservation_id = ?",
                   (reservation_id,))
    return cursor.fetchall()


def room_to_list_of_dict(room):
    room_list = []
    for row in room:
        room_list.append(Database.get_connection().to_dict(row))
    return room_list


def to_dict(self, row):
    return {"id": row[0], "titre": row[1], "identifiant": row[2],
            "auteur": row[3], "date_publication": row[4],
            "paragraphe": row[5]}
