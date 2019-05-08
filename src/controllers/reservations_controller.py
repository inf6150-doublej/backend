from db.database import Database


def save(id, user_id, salle_id):
    connection = Database.get_connection()
    connection.execute(("INSERT INTO reservations(id, user_id, salle_id, date_creation) VALUES(?, ?, ?)"), (id, user_id, salle_id))
    connection.commit()


def delete(id):
    connection = Database.get_connection()
    connection.execute("DELETE FROM reservations WHERE id=?", (id,))
    connection.commit()

