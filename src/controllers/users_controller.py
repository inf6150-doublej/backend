import os, sys
sys.path.append(os.path.abspath(os.path.join('..', '..', '..', 'inf6150')))
from db.database import Database


def create(username, name, family_name, phone, address, email, salt, hashed_password):
    connection = Database.get_connection()
    connection.execute((
        "INSERT INTO Users(username, name, family_name, "
        "phone, address, email, salt, hash)"
        " VALUES(?, ?, ?, ?, ?, ?, ?, ?)"),
        (username, name, family_name, phone, address, email, salt, hashed_password))
    connection.commit()


def delete(username):
    connection = Database.get_connection()
    connection.execute("DELETE FROM Users WHERE username=?", (username,))
    connection.commit()


def update(id, username, name, family_name, phone, address, email, salt, hash, session_username):
    connection = Database.get_connection()
    connection.execute('UPDATE Users '
                        'SET username=?, name=?, family_name=?, phone=?, '
                        'address=?, email=?, salt=?, hash=? '
                        'WHERE id=?',
                        (username, name, family_name, phone, address, email, salt, hash, id,))
    connection.commit()

    # user wants to update his username
    if session_username != username:
        connection.execute('UPDATE sessions '
                            'SET username=?'
                            'WHERE username=?',
                            (username, session_username,))
        connection.commit()


def select_user_id_by_email(email):
    cursor = Database.get_connection().cursor()
    cursor.execute('SELECT id FROM Users WHERE username=?', (email,))
    user = cursor.fetchone()
    if user is None:
        return None
    else:
        return user[0]


def select_user_hash_by_username(username):
    cursor = Database.get_connection().cursor()
    cursor.execute('SELECT salt, hash FROM Users WHERE username=?', (username,))
    user = cursor.fetchone()
    if user is None:
        return None
    else:
        return user[0], user[1]


def select_user_info_by_username(username):
    cursor = Database.get_connection().cursor()
    cursor.execute('SELECT * FROM Users WHERE username=?', (username,))
    user = cursor.fetchone()
    if user is None:
        return None
    else:
        return user[0], user[1], user[2], user[3], user[4], user[5], user[6]


def select_user_username_by_email(email):
    cursor = Database.get_connection().cursor()
    cursor.execute('SELECT username FROM Users WHERE email=?', (email,))
    user = cursor.fetchone()
    if user is None:
        return None
    else:
        return user[0]


def select_user_email_by_username(username):
    cursor = Database.get_connection().cursor()
    cursor.execute('SELECT email FROM Users u WHERE u.username=?',
                    (username,))
    email = cursor.fetchone()
    return email[0]


def select_user_id_by_id_session(id_session):
    cursor = Database.get_connection().cursor()
    cursor.execute('SELECT DISTINCT  u.id '
                    'FROM sessions s JOIN Users u '
                    'ON s.username = u.username '
                    'WHERE id_session=?', (id_session,))
    data = cursor.fetchone()
    if data is None:
        return None
    else:
        return data[0]


def select_all():
    connection = Database.get_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Users')
    return cursor.fetchall()


def update_password(id, salt, hash):
    connection = Database.get_connection()
    connection.execute('UPDATE Users SET salt=?, hash=? WHERE id=?', (salt, hash, id,))
    connection.commit()

   