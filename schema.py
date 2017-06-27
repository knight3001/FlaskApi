from flask import Flask

from general import get_db

app = Flask(__name__)

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
        print('Database Schema Created Succeffully!')

if __name__ == '__main__':
    init_db()
