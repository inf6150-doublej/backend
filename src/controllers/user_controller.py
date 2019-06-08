import os, sys
sys.path.append(os.path.abspath(os.path.join('..', '..', '..', 'backend')))
from db.database import Database

# Create new user
def create(username, email, name, family_name, phone, address, salt, hash, admin):
    connection = Database.get_connection()
    connection.execute((
        "INSERT INTO User(username, name, family_name, "
        "phone, address, email, salt, hash, admin)"
        " VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)"),
        (username, name, family_name, phone, address, email, salt, hash, admin))
    connection.commit()

# Delete a user
def delete(id):
    connection = Database.get_connection()
    connection.execute("DELETE FROM User WHERE id=?", (id,))
    connection.commit()

# Update a user
def update(id, username, email, name, family_name, phone, address, admin):
    connection = Database.get_connection()
    connection.execute('UPDATE User '
                        'SET username=?, email=?, name=?, family_name=?, phone=?, '
                        'address=?, admin=?'
                        'WHERE id=?',
                        (username, email, name, family_name, phone, address, admin, id,))
    connection.commit()

# Find a user by e-mail
def select_user_by_email(email):
    cursor = Database.get_connection().cursor()
    cursor.execute('SELECT * FROM User WHERE email=?', (email,))
    user = cursor.fetchone()
    if user is None:
        return None
    else:
        return user

# Get salt
def get_id_salt(id):
    cursor = Database.get_connection().cursor()
    cursor.execute('SELECT salt FROM User WHERE id=?', (id,))
    user = cursor.fetchone()
    if user is None:
        return None
    else:       
        return user[0]

# Get hash password
def get_id_hash(id):
    cursor = Database.get_connection().cursor()
    cursor.execute('SELECT hash FROM User WHERE id=?', (id,))
    user = cursor.fetchone()
    if user is None:
        return None
    else:       
        return user[0]

# Get all users
def select_all():
    connection = Database.get_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM User')
    users = to_list_of_dict(cursor.fetchall())
    return users

# Update a password
def update_password(id, hash_password):
    print(id)
    print(hash_password)
    connection = Database.get_connection()
    connection.execute('UPDATE User SET hash=? WHERE id=?', (hash_password, id,))
    connection.commit()

# Convert a user list to dictionary
def to_list_of_dict(users):
    room_list = []
    for row in users:
        room_list.append(to_dict(row))
    return room_list

# Convert a user to json object
def to_dict(row):
    return {"id": row[0], "username": row[1], "email": row[2],
            "name": row[3], "family_name": row[4],
            "phone": row[5], "address": row[6], "admin": row[9], }