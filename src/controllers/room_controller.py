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
    cursor.execute("DELETE FROM Equipment WHERE room_id=?", (id,))
    connexion.commit()


def update(id, name, type, capacity, description, equipment, city, postal_code):
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    sql_query = "UPDATE Room " \
        "SET name=?, type=?, capacity=?, description=?, city=?, postalCode=? "\
        "WHERE id=?"
    cursor.execute(sql_query, (name, type, capacity, description, city, postal_code, id,))
    sql_query = "UPDATE Equipment " \
        "SET computer=?, white_board=?, sound_system=?, " \
        "projector=?" \
        "WHERE room_id=?"
    cursor.execute(sql_query,  (equipment["computer"], equipment["white_board"], equipment["sound_system"], equipment["projector"],id, ))
    connexion.commit()
    return cursor.fetchone()


def create(name, type, capacity, description, equipment, city, postal_code):
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    cursor.execute(
        "INSERT INTO Room(name, type, capacity, description, city, postalCode) "
        "VALUES(?, ?, ?, ?, ?, ?)",
        (name, type, capacity, description, city, postal_code))
    room_id = cursor.lastrowid
    cursor.execute(
        "INSERT INTO Equipment(room_id, computer, white_board, "
        "sound_system,projector) "
        "VALUES(?, ?, ?, ?, ?)",
        (room_id, equipment["computer"], equipment["white_board"], equipment["sound_system"], equipment["projector"],))
    connexion.commit()
    return cursor.lastrowid


def select_by_id(id):
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    sql = "SELECT * FROM Room r JOIN Equipment e on r.id =?"
    cursor.execute((sql), (id,))
    return cursor.fetchone()


def select_by_type(type):
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    sql = "SELECT * FROM Room r WHERE r.type =? "
    cursor.execute((sql), (type,))
    return cursor.fetchall()


def select_all():
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    cursor.execute('SELECT * FROM Room r JOIN Equipment e on r.id = e.room_id')
    return cursor.fetchall()


def select_all_available(location, capacity, begin, end, equipment, room_type, postalCode):
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    equipment_sql = build_equipment_sql(equipment)
    sql = "select * from Room r JOIN Equipment e ON r.id = e.room_id WHERE r.id NOT IN "\
    "(select room_id from (select * from Room ro JOIN Reservation re ON ro.id = re.room_id) " \
    "WHERE date_begin >= ? AND date_end <= ?) "\
    "AND r.capacity >= ? AND r.name like ? AND r.postalCode = ? " + equipment_sql
    if room_type != 0:
        type_sql = ' AND r.type = ' + str(room_type)
        sql += type_sql   
    cursor.execute(sql, (begin, end, capacity, location, postalCode,))
    return cursor.fetchall()

def select_all_available_capacityexceeded(location, capacity, begin, end, equipment, room_type):
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    equipment_sql = build_equipment_sql(equipment)
    sql = "select * from Room r JOIN Equipment e ON r.id = e.room_id WHERE r.id NOT IN "\
    "(select room_id from (select * from Room ro JOIN Reservation re ON ro.id = re.room_id) " \
    "WHERE date_begin >= ? AND date_end <= ?) "\
    "AND r.capacity < ?" + equipment_sql
    if room_type != 0:
        type_sql = ' AND r.type = ' + str(room_type)
        sql += type_sql  

    sql += " order by r.capacity desc LIMIT 1 "

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
    cursor.execute("SELECT * FROM Room r JOIN Equipment e on r.id = e.room_id WHERE r.name==?", (name,))
    return cursor.fetchone()


def select_by_reservation_id(reservation_id):
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    cursor.execute("SELECT * FROM Room r JOIN Equipment e on r.id = e.room_id WHERE r.reservation_id = ?",
                   (reservation_id,))
    return cursor.fetchall()


def room_to_list_of_dict(rooms):
    room_list = []
    for row in rooms:
        room_list.append(to_dict(row))
    return room_list


def to_dict(row):
    return {"id": row[0], "name": row[1], "type": row[2],
            "capacity": row[3], "description": row[4], "city": row[5], "postalCode": row[6],
            "equipment": {"computer": row[8],"white_board": row[9],"sound_system": row[10],"projector": row[11]}}

def select_usage(startDate, endDate):
    connexion = Database.get_connection()
    cursor = connexion.cursor()

    cursor.execute("Select sum(computer) computer, sum(white_board) white_board, sum(sound_system) sound_system, sum(projector) projector "\
                    "from Room r "\
                    "inner join equipment e on r.equipment_id = e.id")

    usageTotal = cursor.fetchone()
    if usageTotal is None:
        return None

    cursor.execute("Select sum(computer) computer, sum(white_board) white_board, sum(sound_system) sound_system, sum(projector) projector "\
                    "from Room r "\
                    "inner join equipment e on r.equipment_id = e.id "\
                    "Inner join Reservation rsv on  rsv.room_id = r.id "\
                    "WHERE date_begin >= ? AND date_end <= ? ", (startDate, endDate,) )

    usageReserve = cursor.fetchone()
    if usageReserve is None:
        return None

    return [usageTotal, usageReserve]

def usage_to_dict(usageArray):
    print(usageArray)

    usageTotal = usageArray[0]
    usageReserve = usageArray[1]

    computer = usageTotal[0]
    if usageReserve[0] is None:
        computer = 0
    elif computer != 0:
        computer = usageReserve[0] / computer

    white_board = usageTotal[1]
    if usageReserve[1] is None:
        white_board = 0
    elif white_board != 0:
        white_board = usageReserve[1] / white_board

    sound_system = usageTotal[2]
    if usageReserve[2] is None:
        sound_system = 0
    elif sound_system != 0:
        sound_system = usageReserve[2] / sound_system

    projector = usageTotal[3]
    if usageReserve[3] is None:
        projector = 0
    elif projector != 0:
        projector = usageReserve[3] / projector

    return {"computer": computer, "white_board": white_board,
            "sound_system": sound_system, "projector": projector}


def get_province_postal_code(postalCode):

    if postalCode is None:
        return None

    if postalCode == "":
        return None
    
    firstLetter = postalCode[0].upper()

    if firstLetter == "T":
        return "AB"

    if firstLetter == "V":
        return "CB"

    if firstLetter == "R":
        return "MB"

    if firstLetter == "E":
        return "NB"

    if firstLetter == "A":
        return "NL"
        
    if firstLetter == "B":
        return "NS"

    if firstLetter == "X":
        return "NT"

    if firstLetter == "K" or firstLetter == "L" or firstLetter == "M" or firstLetter == "N" or firstLetter == "P":
        return "ON"

    if firstLetter == "G" or firstLetter == "H" or firstLetter == "J":
        return "QC"

    if firstLetter == "S":
        return "SK"

    if firstLetter == "Y":
        return "YT"

    if firstLetter == "C":
        return "PE"

    return None

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
