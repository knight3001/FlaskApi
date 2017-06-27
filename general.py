import sqlite3
from flask import Flask, g

DATABASE = 'api.db'

app = Flask(__name__)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = dict_factory
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    con = get_db()
    cur = con.cursor()
    result = cur.execute(query, args)
    rv = result.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def insert_db(query, args=()):
    con = get_db()
    cur = con.cursor()
    cur.execute(query, args)
    con.commit()
    row = query_db('SELECT last_insert_rowid()')
    rowid = row[0]['last_insert_rowid()']
    cur.close()
    return rowid
