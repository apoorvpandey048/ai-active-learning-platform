import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Question

DB_URL = 'sqlite:///ai_active_learning.db'


def init_db():
    engine = create_engine(DB_URL, echo=False)
    Base.metadata.create_all(engine)
    return engine


def seed_questions():
    engine = init_db()
    Session = sessionmaker(bind=engine)
    session = Session()

    sample = [
        {
            'topic': 'Machine Learning Basics',
            'question_text': 'What is the main goal of supervised learning?',
            'options': ['Find structure', 'Predict labeled data', 'Reduce dimensions', 'Generate data'],
            'correct_option': 'Predict labeled data'
        },
        {
            'topic': 'ML Basics',
            'question_text': 'Which algorithm is used for classification?',
            'options': ['K-Means', 'Linear Regression', 'Logistic Regression', 'PCA'],
            'correct_option': 'Logistic Regression'
        },
        {
            'topic': 'Deep Learning',
            'question_text': 'What does CNN stand for?',
            'options': ['Convolutional Neural Network', 'Central Neural Node', 'Concat Neural Net', 'Cascading Net'],
            'correct_option': 'Convolutional Neural Network'
        }
    ]

    for q in sample:
        existing = session.query(Question).filter_by(question_text=q['question_text']).first()
        if not existing:
            session.add(Question(topic=q['topic'], question_text=q['question_text'], options_json=json.dumps(q['options']), correct_option=q['correct_option']))

    session.commit()
    session.close()


if __name__ == '__main__':
    seed_questions()
