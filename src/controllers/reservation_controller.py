from db.database import Database
from sqlite3 import Error

def save(user_id, room_id, begin, end):
    connection = Database.get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(("INSERT INTO Reservation(user_id, room_id, date_begin, date_end) VALUES(?, ?, ?, ?)"), (user_id, room_id, begin, end))
        connection.commit()
        return cursor.lastrowid
    except Error:
        print('error save in Reservation')
        return -1


def update(id, user_id, room_id, begin, end):
    connection = Database.get_connection()
    connection.execute('UPDATE Reservation '
                        'SET user_id=?, room_id=?, date_begin=?, date_end=?, '
                        'WHERE id=?',
                        (user_id, room_id, begin, end, id))
    connection.commit()


def delete(id):
    connection = Database.get_connection()
    connection.execute("DELETE FROM Reservation WHERE id=?", (id,))
    connection.commit()


def select_all():
    connection = Database.get_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Reservation')
    reservations = to_list_of_dict(cursor.fetchall())
    return reservations



def to_list_of_dict(reservations):
    reservation_list = []
    for row in reservations:
        reservation_list.append(to_dict(row))
    return reservation_list


def to_dict(row):
    return {"id": row[0], "user_id": row[1], "room_id": row[2],
            "date_begin": row[3], "date_end": row[4]}