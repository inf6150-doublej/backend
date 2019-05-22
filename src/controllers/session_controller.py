from db.database import Database


def save(id_session, email):
    connection = Database.get_connection()
    connection.execute(("INSERT INTO Session(id_session, email) "
                        "VALUES(?, ?)"), (id_session, email,))
    connection.commit()


def delete(id_session):
    connection = Database.get_connection()
    connection.execute("DELETE FROM Session WHERE id_session=?", (id_session,))
    connection.commit()


def select_user_by_session_id(id_session):
    cursor = Database.get_connection().cursor()
    cursor.execute("SELECT * FROM User u JOIN Session s ON u.email = s.email WHERE id_session=?", (id_session,))
    data = cursor.fetchone()
    if data is None:
        return None
    else:
        return to_dict(data)


def to_dict(row):
    return {"id": row[0], "username": row[1], "email": row[2],
            "name": row[3], "family_name": row[4],
            "phone": row[5], "address": row[6], "admin": row[9]} 