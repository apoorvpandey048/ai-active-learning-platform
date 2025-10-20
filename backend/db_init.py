import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Lecture, Question
from faker import Faker
import random

DB_URL = 'sqlite:///ai_active_learning.db'


def init_db():
    engine = create_engine(DB_URL, echo=False)
    Base.metadata.create_all(engine)
    return engine


def seed_questions():
    fake = Faker()
    engine = init_db()
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create sample users
    users = []
    for _ in range(3):
        u = User(name=fake.name(), email=fake.unique.email())
        session.add(u)
        users.append(u)

    session.commit()

    # Create sample lectures
    lectures = []
    for i in range(3):
        title = f"Intro to Topic {i+1}"
        url = f"https://youtu.be/dummy{i+1}"
        transcript = ' '.join([fake.paragraph() for _ in range(5)])
        summary = ' '.join([fake.sentence() for _ in range(2)])
        lec = Lecture(title=title, yt_url=url, transcript=transcript, summary=summary)
        session.add(lec)
        lectures.append(lec)

    session.commit()

    # Create questions: 15 per lecture
    for lec in lectures:
        for qn in range(15):
            question_text = fake.sentence(nb_words=10)
            options = [fake.word() for _ in range(4)]
            correct = random.choice(options)
            question = Question(lecture_id=lec.id, question_text=question_text, options=json.dumps(options), correct_answer=correct)
            session.add(question)

    session.commit()
    session.close()


if __name__ == '__main__':
    seed_questions()
