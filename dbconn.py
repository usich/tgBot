import sqlite3

with sqlite3.connect('database.db') as conn:
    cursor = conn.cursor()
