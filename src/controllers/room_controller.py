import os
import sys
import datetime
sys.path.append(os.path.abspath(os.path.join('..', 'backend')))
sys.path.append(os.path.abspath(os.path.join('..', '..')))
from binascii import a2b_base64
from db.database import Database
import sqlite3


def delete(id):
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    cursor.execute("DELETE FROM Room WHERE id=?", (id,))
    connexion.commit()


def update(id, name, type, capacity, description, equipment_id):
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    sql_query = "UPDATE Room " \
        "SET name=?, type=?, capacity=?, description=?, " \
        "equipment_id=?" \
        "WHERE id=?"
    cursor.execute(sql_query, (name, type, capacity, description, equipment_id, id,))
    connexion.commit()
    return cursor.fetchone()


def create(name, type, capacity, description, equipment_id):
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    cursor.execute(
        "INSERT INTO Room(name, type, capacity, "
        "description,equipment_id) "
        "VALUES(?, ?, ?, ?, ?)",
        (name, type, capacity, description, equipment_id,))
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


def select_all_available(capacity, begin, end, equipment):
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    equipment_sql = build_equipment_sql(equipment)
    sql = "select * from Room r JOIN Equipment e ON r.id = e.room_id WHERE r.id NOT IN "\
    "(select room_id from (select * from Room ro JOIN Reservation re ON ro.id = re.room_id) " \
    "WHERE date_begin >= ? AND date_end <= ?) "\
    "AND r.capacity >= ?" + equipment_sql
    cursor.execute(sql, (begin, end, capacity,))
    return cursor.fetchall()


def build_equipment_sql(equipment):
    sql = ''
    for key, value in equipment.items():
        if key == 'soundsystem' and value is True:
            sql += ' AND e.sound_system = 1'
        elif key == 'whiteboard' and value is True:
            sql += ' AND e.white_board = 1'
        elif key == 'projector' and value is True:
            sql += ' AND e.projector = 1'
        elif key == 'computer' and value is True:
            sql += ' AND e.computer = 1'
    return sql


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
            "equipment_id": row[5]}



# to test uncomment and  => cd backend/src/room_controler && python3 room_controler.py
# def print_res(data):
#     print('')
#     # for row in data:
#     #     print(row)
#     #     print('\n')


# capacity = 50
# begin= '2019 05 28 07:30:00'
# end='2019 05 28 08:30:00'
# equipment=None
# begin = datetime.datetime.strptime(begin, "%Y %m %d %H:%M:%S")
# end = datetime.datetime.strptime(end, "%Y %m %d %H:%M:%S")
# res = select_all_available(capacity, begin, end, equipment)
# print_res(res)
