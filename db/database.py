# coding: utf8

import sqlite3
from binascii import a2b_base64
import os


class Database:
    __instance = None

    @staticmethod
    def get_connection():
        if Database.__instance == None:
            Database()
        return Database.__instance.connection

    def __init__(self):
        if Database.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Database.__instance = self
            current_path = os.path.abspath(os.path.dirname(__file__))
            path = os.path.join(current_path, 'db.db')
            self.connection = sqlite3.connect(path, check_same_thread=False)


    def disconnect(self):
        if self.connection is not None:
            self.connection.close()
