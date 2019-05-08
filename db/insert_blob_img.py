import datetime
import sqlite3
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOT_DIR, 'db.db')

con = sqlite3.connect(DB_PATH)
cur = con.cursor()
now = datetime.datetime.now()

with open(ROOT_DIR + '/img/bear.jpeg', "rb") as input_file:
    imagedata = input_file.read()
pic_id = 'ju'
img_data = sqlite3.Binary(imagedata)
cur.execute('INSERT INTO Pictures'
            '(pic_id, img_data)'
            ' VALUES (?,?)', (pic_id, img_data))
con.commit()

with open(ROOT_DIR + '/img/squirel.jpeg', "rb") as input_file:
    imagedata = input_file.read()
pic_id = 'frank'
img_data = sqlite3.Binary(imagedata)
cur.execute('INSERT INTO Pictures'
            '(pic_id, img_data)'
            ' VALUES (?,?)', (pic_id, img_data))
con.commit()

with open(ROOT_DIR + '/img/panda.jpeg', "rb") as input_file:
    imagedata = input_file.read()
pic_id = 'luce'
img_data = sqlite3.Binary(imagedata)
cur.execute('INSERT INTO Pictures'
            '(pic_id, img_data)'
            ' VALUES (?,?)', (pic_id, img_data))
con.commit()

with open(ROOT_DIR + '/img/zebra.jpeg', "rb") as input_file:
    imagedata = input_file.read()
pic_id = 'renee'
img_data = sqlite3.Binary(imagedata)
cur.execute('INSERT INTO Pictures'
            '(pic_id, img_data)'
            ' VALUES (?,?)', (pic_id, img_data))
con.commit()

with open(ROOT_DIR + '/img/elephant.jpeg', "rb") as input_file:
    imagedata = input_file.read()
pic_id = 'michelle'
img_data = sqlite3.Binary(imagedata)
cur.execute('INSERT INTO Pictures'
            '(pic_id, img_data)'
            ' VALUES (?,?)', (pic_id, img_data))

with open(ROOT_DIR + '/img/cat1.jpeg', "rb") as input_file:
    imagedata = input_file.read()
pic_id = 'claude'
img_data = sqlite3.Binary(imagedata)
cur.execute('INSERT INTO Pictures'
            '(pic_id, img_data)'
            ' VALUES (?,?)', (pic_id, img_data))
con.commit()

with open(ROOT_DIR + '/img/cat2.jpeg', "rb") as input_file:
    imagedata = input_file.read()
pic_id = 'flavie'
img_data = sqlite3.Binary(imagedata)
cur.execute('INSERT INTO Pictures'
            '(pic_id, img_data)'
            ' VALUES (?,?)', (pic_id, img_data))
con.commit()

with open(ROOT_DIR + '/img/cat3.jpeg', "rb") as input_file:
    imagedata = input_file.read()
pic_id = 'machtelle'
img_data = sqlite3.Binary(imagedata)
cur.execute('INSERT INTO Pictures'
            '(pic_id, img_data)'
            ' VALUES (?,?)', (pic_id, img_data))
con.commit()

with open(ROOT_DIR + '/img/cat4.jpeg', "rb") as input_file:
    imagedata = input_file.read()
pic_id = 'mutante'
img_data = sqlite3.Binary(imagedata)
cur.execute('INSERT INTO Pictures'
            '(pic_id, img_data)'
            ' VALUES (?,?)', (pic_id, img_data))
con.commit()

with open(ROOT_DIR + '/img/cat5.jpeg', "rb") as input_file:
    imagedata = input_file.read()
pic_id = 'vincent'
img_data = sqlite3.Binary(imagedata)
cur.execute('INSERT INTO Pictures'
            '(pic_id, img_data)'
            ' VALUES (?,?)', (pic_id, img_data))
con.commit()

with open(ROOT_DIR + '/img/cat6.jpeg', "rb") as input_file:
    imagedata = input_file.read()
pic_id = 'etienne'
img_data = sqlite3.Binary(imagedata)
cur.execute('INSERT INTO Pictures'
            '(pic_id, img_data)'
            ' VALUES (?,?)', (pic_id, img_data))
con.commit()

with open(ROOT_DIR + '/img/cat7.jpeg', "rb") as input_file:
    imagedata = input_file.read()
pic_id = 'elie'
img_data = sqlite3.Binary(imagedata)
cur.execute('INSERT INTO Pictures'
            '(pic_id, img_data)'
            ' VALUES (?,?)', (pic_id, img_data))
con.commit()

with open(ROOT_DIR + '/img/dog1.jpeg', "rb") as input_file:
    imagedata = input_file.read()
pic_id = 'auguste'
img_data = sqlite3.Binary(imagedata)
cur.execute('INSERT INTO Pictures'
            '(pic_id, img_data)'
            ' VALUES (?,?)', (pic_id, img_data))
con.commit()

with open(ROOT_DIR + '/img/dog2.jpeg', "rb") as input_file:
    imagedata = input_file.read()
pic_id = 'gloria'
img_data = sqlite3.Binary(imagedata)
cur.execute('INSERT INTO Pictures'
            '(pic_id, img_data)'
            ' VALUES (?,?)', (pic_id, img_data))
con.commit()

with open(ROOT_DIR + '/img/dog3.jpeg', "rb") as input_file:
    imagedata = input_file.read()
pic_id = 'marc'
img_data = sqlite3.Binary(imagedata)
cur.execute('INSERT INTO Pictures'
            '(pic_id, img_data)'
            ' VALUES (?,?)', (pic_id, img_data))
con.commit()

with open(ROOT_DIR + '/img/dog4.jpeg', "rb") as input_file:
    imagedata = input_file.read()
pic_id = 'david'
img_data = sqlite3.Binary(imagedata)
cur.execute('INSERT INTO Pictures'
            '(pic_id, img_data)'
            ' VALUES (?,?)', (pic_id, img_data))
con.commit()

con.close()
