from sqlalchemy import Column, Integer, ForeignKey, Table, Boolean, String
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

chat_user = Table(
    "chat_user",
    Base.metadata,
    Column("chat_id", Integer, ForeignKey("chat.chat_id")),
    Column("user_id", Integer, ForeignKey("user.user_id")),
)


class Chat(Base):
    __tablename__ = 'chat'
    chat_id = Column(Integer, primary_key=True)
    is_enabled = Column(Boolean)
    messages_decoded = Column(Integer)
    users = relationship('User', backref=backref('chat'))


class User(Base):
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True)
    messages_decoded = Column(Integer)
    chats = relationship('Chat', backref=backref('user'))


class Locale(Base):
    __tablename__ = 'locale'
    text_meta = Column(String, primary_key=True)
    lang = Column(String)
    text = Column(String)
