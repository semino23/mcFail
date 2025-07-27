import sqlite3

DATABASE = "test.sqlite"


def collect_player():
    cur = sqlite3.connect(DATABASE).cursor()
    players = cur.execute("SELECT * FROM players").fetchmany()
    print(players)
