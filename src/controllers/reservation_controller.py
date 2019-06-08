from db.database import Database
from sqlite3 import Error

# Create a reservation
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

# Update a reservation
def update(id, user_id, room_id, begin, end):
    connection = Database.get_connection()
    cursor = connection.cursor()
    sql_query = "UPDATE Reservation " \
                "SET user_id=?, room_id=?, date_begin=?, date_end=? " \
                "WHERE id=?"
    cursor.execute(sql_query, (user_id, room_id, begin, end, id))
    connection.commit()
    return cursor.fetchone()

# Delete a reservation
def delete(id):
    connection = Database.get_connection()
    connection.execute("DELETE FROM Reservation WHERE id=?", (id,))
    connection.commit()

# Get All reservations
def select_all():
    connection = Database.get_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT re.id, re.user_id, re.room_id, re.date_begin, re.date_end, ro.name, u.name, u.family_name FROM Reservation re JOIN User u on u.id = re.user_id JOIN Room ro on ro.id = re.room_id' )
    reservations = to_list_of_dict(cursor.fetchall())
    return reservations

# Get a reservation by id
def select_by_id(id):
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    sql = "SELECT * FROM Reservation s WHERE s.id == ? "
    cursor.execute((sql), (id,))
    return cursor.fetchone()

# Convert reservation list to dictionary
def to_list_of_dict(reservations):
    reservation_list = []
    for row in reservations:
        reservation_list.append(to_dict(row))
    return reservation_list

# Convert database row to json object
def to_dict(row):
    return {"id": row[0], "user_id": row[1], "room_id": row[2],
            "date_begin": row[3], "date_end": row[4], "room_name": row[5], "user_name": row[6], "user_family_name": row[7],}