import os
import sqlite3
from sqlalchemy import create_engine, select, update
from models import Base


class Db:
    DB_FILE = 'db.bin'
    ENGINE = create_engine(f'sqlite:///{DB_FILE}')

    @staticmethod
    def __init__():
        if not os.path.exists(Db.DB_FILE):
            conn = None
            try:
                conn = sqlite3.connect(Db.DB_FILE)
                print(sqlite3.version)
            except sqlite3.Error as e:
                print(e)
            finally:
                if conn:
                    conn.close()

    @staticmethod
    def makemigrations():
        pass
