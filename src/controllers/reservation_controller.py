from db.database import Database


def save(id, user_id, room_id):
    connection = Database.get_connection()
    connection.execute(("INSERT INTO Reservation(id, user_id, room_id, date_creation) VALUES(?, ?, ?)"), (id, user_id, room_id))
    connection.commit()


def delete(id):
    connection = Database.get_connection()
    connection.execute("DELETE FROM Reservation WHERE id=?", (id,))
    connection.commit()

