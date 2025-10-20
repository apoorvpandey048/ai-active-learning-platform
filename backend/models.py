from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
import json

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    email = Column(String(256), nullable=False, unique=True)
    mastery = Column(Integer, default=0)
    accuracy = Column(Integer, default=0)


class Lecture(Base):
    __tablename__ = 'lectures'
    id = Column(Integer, primary_key=True)
    title = Column(String(256))
    yt_url = Column(String(512))
    transcript = Column(Text)
    summary = Column(Text)


class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    lecture_id = Column(Integer, ForeignKey('lectures.id'), nullable=True)
    question_text = Column(Text, nullable=False)
    options = Column(Text, nullable=False)  # JSON encoded list
    correct_answer = Column(String(256), nullable=False)

    lecture = relationship('Lecture')


class QuizResult(Base):
    __tablename__ = 'quiz_results'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    lecture_id = Column(Integer, ForeignKey('lectures.id'))
    score = Column(Integer)
    date = Column(DateTime, server_default=func.now())

    user = relationship('User')
    lecture = relationship('Lecture')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'lecture_id': self.lecture_id,
            'score': self.score,
            'date': self.date.isoformat() if self.date else None,
        }

