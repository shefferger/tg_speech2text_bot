import os
import sqlite3
from contextlib import contextmanager
import sqlalchemy.util
from sqlalchemy import create_engine, orm, insert, update
import models


class Db:
    DB_FILE = 'db.sqlite3'
    ENGINE = create_engine(f'sqlite:///{DB_FILE}')
    Session = orm.sessionmaker(bind=ENGINE)

    @staticmethod
    def __init__():
        if not os.path.exists(Db.DB_FILE):
            conn = None
            try:
                conn = sqlite3.connect(Db.DB_FILE)
                models.Base.metadata.create_all(Db.ENGINE)
            except sqlite3.Error as e:
                print(e)
            finally:
                if conn:
                    conn.close()

    @staticmethod
    @contextmanager
    def get_session_rw():
        with Db.Session() as session:
            try:
                yield session
            except Exception as exc:
                print(exc)
                session.rollback()

    @staticmethod
    def update_locale(text_meta: str, lang: str, text: str) -> str:
        data = Db.get_locale(text_meta, lang)
        if data is None:
            with Db.get_session_rw() as session:
                query = insert(models.Locale).values(text_meta=f'{text_meta}_{lang}', lang=lang, text=text)
                session.execute(query)
                session.commit()
        elif data != text:
            with Db.get_session_rw() as session:
                session.query(models.Locale).filter_by(text_meta=f'{text_meta}_{lang}').update(dict(text=text))
                session.commit()
        return text

    @staticmethod
    def get_locale(text_meta: str, lang: str) -> str:
        with Db.get_session_rw() as session:
            data = session.query(models.Locale).filter_by(text_meta=f'{text_meta}_{lang}').first()
            return data.text if data else None

    @staticmethod
    def set_status(chat_id: int, is_enabled: bool, lang: str):
        with Db.get_session_rw() as session:
            if session.query(models.Chat).filter_by(chat_id=chat_id).first():
                session.query(models.Chat).filter_by(chat_id=chat_id).update(dict(is_enabled=is_enabled,
                                                                                  lang=lang))
            else:
                query = insert(models.Chat).values(chat_id=chat_id,
                                                   is_enabled=is_enabled,
                                                   msgs_decoded=0,
                                                   lang=lang)
                session.execute(query)
            session.commit()

    @staticmethod
    def get_status(chat_id: int) -> dict:
        with Db.get_session_rw() as session:
            data = session.query(models.Chat).filter_by(chat_id=chat_id).first()
            if data is sqlalchemy.util.NoneType:
                Db.set_status(chat_id=chat_id, is_enabled=False, lang='en')
            return dict(is_enabled=data.is_enabled, msgs_decoded=data.msgs_decoded, lang=data.lang)\
                if data else dict(is_enabled=False, msgs_decoded=0, lang=None)

    @staticmethod
    def set_user(chat_id: int, user_id: int, lang: str):
        pass

    @staticmethod
    def get_user() -> dict:
        pass

    @staticmethod
    def decode_msg(chat_id: int, user_id: int):
        pass
