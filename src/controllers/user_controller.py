import os, sys
sys.path.append(os.path.abspath(os.path.join('..', '..', '..', 'backend')))
from db.database import Database


def create(username, email, name, family_name, phone, address, salt, hash, admin):
    connection = Database.get_connection()
    connection.execute((
        "INSERT INTO User(username, name, family_name, "
        "phone, address, email, salt, hash)"
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


def update(id, username, email, name, family_name, phone, address, salt, hash, admin):
    connection = Database.get_connection()
    connection.execute('UPDATE User '
                        'SET username=?, email=?, name=?, family_name=?, phone=?, '
                        'address=?, salt=?, hash=?, admin=?'
                        'WHERE id=?',
                        (username, name, family_name, phone, address, email, salt, hash, admin, id,))
    connection.commit()


def select_user_by_email(email):
    cursor = Database.get_connection().cursor()
    cursor.execute('SELECT * FROM User WHERE email=?', (email,))
    user = cursor.fetchone()
    if user is None:
        return None
    else:
        return user


def select_all():
    connection = Database.get_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM User')
    return cursor.fetchall()


def update_password(id, salt, hash):
    connection = Database.get_connection()
    connection.execute('UPDATE User SET salt=?, hash=? WHERE id=?', (salt, hash, id,))
    connection.commit()
