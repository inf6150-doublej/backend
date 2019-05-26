import os, sys
sys.path.append(os.path.abspath(os.path.join('..', '..', '..', 'backend')))
from db.database import Database


def create(username, email, name, family_name, phone, address, salt, hash, admin):
    connection = Database.get_connection()
    connection.execute((
        "INSERT INTO User(username, name, family_name, "
        "phone, address, email, salt, hash, admin)"
        " VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)"),
        (username, name, family_name, phone, address, email, salt, hash, admin))
    connection.commit()


def delete(id):
    connection = Database.get_connection()
    connection.execute("DELETE FROM User WHERE id=?", (id,))
    connection.commit()


def delete_by_email(email):
    connection = Database.get_connection()
    connection.execute("DELETE FROM User WHERE email=?", (email,))
    connection.commit()


def update(id, username, email, name, family_name, phone, address, admin):
    connection = Database.get_connection()
    connection.execute('UPDATE User '
                        'SET username=?, email=?, name=?, family_name=?, phone=?, '
                        'address=?, admin=?'
                        'WHERE id=?',
                        (username, name, family_name, phone, address, email, admin, id,))
    connection.commit()


def select_user_by_email(email):
    cursor = Database.get_connection().cursor()
    cursor.execute('SELECT * FROM User WHERE email=?', (email,))
    user = cursor.fetchone()
    if user is None:
        return None
    else:
        user = to_dict(user)
        return user

def get_id_salt(id):
    cursor = Database.get_connection().cursor()
    cursor.execute('SELECT salt FROM User WHERE id=?', (id,))
    user = cursor.fetchone()
    if user is None:
        return None
    else:       
        return user[0]

def get_id_hash(id):
    cursor = Database.get_connection().cursor()
    cursor.execute('SELECT hash FROM User WHERE id=?', (id,))
    user = cursor.fetchone()
    if user is None:
        return None
    else:       
        return user[0]

def select_all():
    connection = Database.get_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM User')
    users = to_list_of_dict(cursor.fetchall())
    return users


def update_password(id, salt, hash):
    connection = Database.get_connection()
    connection.execute('UPDATE User SET salt=?, hash=? WHERE id=?', (salt, hash, id,))
    connection.commit()


def to_list_of_dict(users):
    room_list = []
    for row in users:
        room_list.append(to_dict(row))
    return room_list


def to_dict(row):
    return {"id": row[0], "username": row[1], "email": row[2],
            "name": row[3], "family_name": row[4],
            "phone": row[5], "address": row[6], "admin": row[9], }