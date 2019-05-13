import os, sys, sqlite3
sys.path.append(os.path.abspath(os.path.join('..', 'backend')))
from db.database import Database
from binascii import a2b_base64

def select(pic_id):
    cursor = Database.get_connection().cursor()
    cursor.execute(("SELECT img_data FROM Picture WHERE pic_id=?"), (pic_id,))
    picture = cursor.fetchone()
    if picture is None:
        return None
    else:
        blob_data = picture[0]
        return blob_data


def insert(pic_id, file_data):
    listed_img_uri = file_data.split(',')
    img_base64_tostring = listed_img_uri[1]

    # convert string to binary data for writing purpose
    binary_data = a2b_base64(img_base64_tostring)
    connection = Database.get_connection()
    connection.execute(
        "INSERT INTO Picture(pic_id, img_data) VALUES(?, ?)",
        [pic_id, sqlite3.Binary(binary_data)])
    connection.commit()


def update(pic_id, file_data):
    listed_img_uri = file_data.split(',')
    img_base64_tostring = listed_img_uri[1]

    # convert string to binary data for writing purpose
    binary_data = a2b_base64(img_base64_tostring)
    connection = Database.get_connection()
    connection.execute("UPDATE Picture SET img_data = ? WHERE pic_id = ?", [sqlite3.Binary(binary_data), pic_id])
    connection.commit()
