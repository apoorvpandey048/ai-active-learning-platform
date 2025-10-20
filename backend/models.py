from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.types import JSON

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    email = Column(String(256), nullable=False, unique=True)


class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    topic = Column(String(128), nullable=False)
    question_text = Column(Text, nullable=False)
    options_json = Column(Text, nullable=False)  # store JSON string
    correct_option = Column(String(256), nullable=False)


class Progress(Base):
    __tablename__ = 'progress'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    week = Column(String(64))
    mastery = Column(Integer)
    engagement = Column(Integer)
    accuracy = Column(Integer)

    user = relationship('User')


class Lecture(Base):
    __tablename__ = 'lectures'
    id = Column(Integer, primary_key=True)
    title = Column(String(256))
    video_url = Column(String(512))
    transcript = Column(Text)
    summary = Column(Text)
