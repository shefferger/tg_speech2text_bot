import os
import sqlite3
from contextlib import contextmanager
from sqlalchemy import create_engine, orm, select, insert, update
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
                query = update(models.Locale).where(models.Locale.text_meta == f'{text_meta}_{lang}').\
                    values(text=text)
                session.execute(query)
                session.commit()
        return text

    @staticmethod
    def get_locale(text_meta: str, lang: str) -> str:
        with Db.get_session_rw() as session:
            query = select(models.Locale).where(models.Locale.text_meta == f'{text_meta}_{lang}')
            data = session.execute(query).first()
            return data[0].text if data else None

    @staticmethod
    def set_status(chat_id: int, is_enabled: bool):
        with Db.get_session_rw() as session:
            if session.query(models.Chat).filter_by(chat_id=chat_id).first():
                session.query(models.Chat).filter_by(chat_id=chat_id).update(dict(is_enabled=is_enabled))
            else:
                query = insert(models.Chat).values(chat_id=chat_id,
                                                   is_enabled=is_enabled,
                                                   msgs_decoded=0)
                session.execute(query)
            session.commit()

    @staticmethod
    def get_status(chat_id: int) -> dict:
        with Db.get_session_rw() as session:
            query = select(models.Chat).where(models.Chat.chat_id == chat_id)
            data = session.execute(query).first()
            if not data:
                Db.set_status(chat_id=chat_id, is_enabled=False)
            return dict(is_enabled=data[0].is_enabled, msgs_decoded=data[0].msgs_decoded)\
                if data else dict(is_enabled=False, msgs_decoded=0)
