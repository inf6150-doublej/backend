import os, sys, sqlite3
sys.path.append(os.path.abspath(os.path.join('..', 'inf6150')))
from db.database import Database
from binascii import a2b_base64


def delete(reservation_id, pic_id):
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    cursor.execute("DELETE FROM Salles WHERE reservation_id=?", (reservation_id,))
    connexion.commit()
    cursor.execute("DELETE FROM Pictures WHERE pic_id=?", (pic_id,))
    connexion.commit()


def update(name, type, date_creation, description, pic_id, reservation_id):
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    if pic_id == '':
        # no need to update image
        sql_query = "UPDATE Salles " \
                    "SET name=?, type=?, race=?, age=?," \
                    " date_creation=?, description=? WHERE reservation_id=?"
        cursor.execute(sql_query,(name, type, date_creation, description, reservation_id,))
    else:
        sql_query = "UPDATE Salles " \
                    "SET name=?, type=?, race=?, age=?, " \
                    "date_creation=?, description=?, pic_id=? " \
                    "WHERE reservation_id=?"
        cursor.execute(sql_query, (name, type, date_creation, description, pic_id, reservation_id,))
    connexion.commit()
    return cursor.fetchone()


def insert(name, type, date_creation, description, pic_id, reservation_id):
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    cursor.execute(
        "INSERT INTO Salles(name, type, date_creation, "
        "description, pic_id, reservation_id) "
        "VALUES(?, ?, ?, ?, ?,?,?, ?)",
        (name, type, date_creation, description, pic_id, reservation_id,))
    connexion.commit()


def select_by_id(id):
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    sql = "SELECT * FROM Salles s WHERE s.id == ? "
    cursor.execute((sql), (id,))
    return cursor.fetchone()


def select_five_random_salles():
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    cursor.execute('SELECT * FROM Salles ORDER BY random() LIMIT 5')
    return cursor.fetchall()

def order_by_date_creation(option):
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    cursor.execute(" SELECT * FROM Salles WHERE "
                    "strftime('%Y-%m-%d','now') >= strftime"
                    "('%Y-%m-%d',date_creation) ORDER BY "
                    "date_creation DESC")
    if option == 1:
        return get_db().salles_to_list_of_dict(cursor.fetchall())
    else:
        return cursor.fetchmany(5)

def select_by_type(type):
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    sql = "SELECT * FROM Salles s WHERE s.type == ? "
    cursor.execute((sql), (type,))
    return cursor.fetchall()

def select_all():
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    cursor.execute('SELECT * FROM Salles')
    return cursor.fetchall()

def select_by_name(name):
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    sql_query = "%" + name + "%"
    cursor.execute("SELECT * FROM Salles WHERE name LIKE ?", (sql_query,))
    return cursor.fetchone()


def select_by_reservation_id(reservation_id):
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    cursor.execute("SELECT * FROM Salles WHERE reservation_id = ?", (reservation_id,))
    return cursor.fetchall()


def select_pic_id_by_reservation_id(reservation_id):
    connexion = Database.get_connection()
    cursor = connexion.cursor()
    cursor.execute("SELECT pic_id FROM Salles WHERE reservation_id = ?",
                    (reservation_id,))
    return cursor.fetchall()


def salle_to_list_of_dict(salle):
    salle_list = []
    for row in salle:
        salle_list.append(get_db().to_dict(row))
    return salle_list


def to_dict(self, row):
    return {"id": row[0], "titre": row[1], "identifiant": row[2],
            "auteur": row[3], "date_publication": row[4],
            "paragraphe": row[5]}    
