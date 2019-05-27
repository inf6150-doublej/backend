import os
import sys
sys.path.append(os.path.abspath(os.path.join('..', 'backend')))
from binascii import a2b_base64
from db.database import Database
import sqlite3


def delete(id):
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    cursor.execute("DELETE FROM Room WHERE id=?", (id,))
    connexion.commit()


def update(id, name, type, capacity, description, reservation_id, equipment_id):
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    sql_query = "UPDATE Room " \
        "SET name=?, type=?, capacity=?, description=?, " \
        "reservation_id=?, equipment_id=?" \
        "WHERE id=?"
    cursor.execute(sql_query, (name, type, capacity, description, reservation_id, equipment_id, id,))
    connexion.commit()
    return cursor.fetchone()


def create(name, type, capacity, description, reservation_id, equipment_id):
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    cursor.execute(
        "INSERT INTO Room(name, type, capacity, "
        "description, reservation_id, equipment_id) "
        "VALUES(?, ?, ?, ?, ?, ?)",
        (name, type, capacity, description, reservation_id, equipment_id,))
    connexion.commit()
    return cursor.lastrowid


def select_by_id(id):
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    sql = "SELECT * FROM Room s WHERE s.id == ? "
    cursor.execute((sql), (id,))
    return cursor.fetchone()


def select_by_type(type):
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    sql = "SELECT * FROM Room r WHERE r.type == ? "
    cursor.execute((sql), (type,))
    return cursor.fetchall()


def select_all():
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    cursor.execute('SELECT * FROM Room')
    return cursor.fetchall()


def select_all_available():
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    cursor.execute('SELECT * FROM Room r WHERE r.reservation_id IS NULL')
    return cursor.fetchall()


def select_by_name(name):
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    cursor.execute("SELECT * FROM Room WHERE name==?", (name,))
    return cursor.fetchone()


def select_by_reservation_id(reservation_id):
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    cursor.execute("SELECT * FROM Room WHERE reservation_id = ?",
                   (reservation_id,))
    return cursor.fetchall()


def room_to_list_of_dict(rooms):
    room_list = []
    for row in rooms:
        room_list.append(to_dict(row))
    return room_list


def to_dict(row):
    return {"id": row[0], "name": row[1], "type": row[2],
            "capacity": row[3], "description": row[4],
            "reservation_id": row[5], "equipment_id": row[6]}
