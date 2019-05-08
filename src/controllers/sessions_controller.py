from db.database import Database


def save(id_session, username):
    connection = Database.get_connection()
    connection.execute(("INSERT INTO Sessions(id_session, username) "
                        "VALUES(?, ?)"), (id_session, username,))
    connection.commit()


def delete(id_session):
    connection = Database.get_connection()
    connection.execute("DELETE FROM Sessions WHERE id_session=?", (id_session,))
    connection.commit()


def get_session_username_by_id_session(id_session):
    cursor = Database.get_connection().cursor()
    cursor.execute("SELECT username FROM Sessions WHERE id_session=?", (id_session,))
    data = cursor.fetchone()
    if data is None:
        return None
    else:
        return data[0]