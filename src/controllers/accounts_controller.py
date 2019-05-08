import os, sys
sys.path.append(os.path.abspath(os.path.join('..', '..', '..', 'inf6150')))
from db.database import Database

def get_account_token_by_username(username):
    connection = Database.get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT token FROM Account WHERE username=?",
                    (username,))
    data = cursor.fetchone()
    if data is None:
        return None
    else:
        return data[0]

def delete(username):
    connection = Database.get_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Account WHERE username=?", (username,))
    connection.commit()

def create(username, user_email, token, date):
    connection = Database.get_connection()
    connection.execute(
        "INSERT INTO Account(username, email,token,date_sent) "
        "VALUES(?, ?, ?, ?)",
        (username, user_email, token, date))
    connection.commit()