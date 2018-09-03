import sqlite3
from datetime import datetime, timedelta


def create_database():
    conn = sqlite3.connect("move.db")
    c = conn.cursor()
    try:
        c.execute("create table move (date text, position real)")
        conn.commit()
        conn.close()
        add_move(datetime.today(), 0.0)
    except sqlite3.OperationalError:
        print("Already exists")


def add_move(date,position):
    conn = sqlite3.connect("move.db")
    c = conn.cursor()
    c.execute("insert into move(date,position) values(?,?)", [date, position])
    conn.commit()
    conn.close()


def get_last_position():
    conn = sqlite3.connect("move.db")
    c = conn.cursor()
    c.execute("select max(position) from move")
    ret = c.fetchone()
    conn.close()

    return ret[0]


def get_all_position():
    conn = sqlite3.connect("move.db")
    c = conn.cursor()
    c.execute("select * from move order by position")
    for row in c:
        print(row)
    conn.close()
