# coding: utf8

# Copyright 2017 Jacques Berger
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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
            self.connection = sqlite3.connect(path)

    # def __init__(self):
    #     self.connection = None

    # def get_connection(self):
    #     if self.connection is None:
    #         current_path = os.path.abspath(os.path.dirname(__file__))
    #         path = os.path.join(current_path, 'db.db')
    #         self.connection = sqlite3.connect(path)
    #     return self.connection

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()
