from db.database import Database


def save(user_id, room_id, begin, end):
    connection = Database.get_connection()
    connection.execute(("INSERT INTO Reservation(user_id, room_id, date_begin, date_end) VALUES(?, ?, ?, ?)"), (user_id, room_id, begin, end))
    connection.commit()


def delete(id):
    connection = Database.get_connection()
    connection.execute("DELETE FROM Reservation WHERE id=?", (id,))
    connection.commit()

