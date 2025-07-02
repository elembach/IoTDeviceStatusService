import sqlite3
from flask import g, current_app

DATABASE = 'database.db'


# Returns database connection and creates one if there is not a current connection
def get_db():
    if "db" not in g:
        # g.db is a SQLite connection object that points to open link in SQLite database file,
        g.db = sqlite3.connect(current_app.config.get("DATABASE", "database.db"))
        # Each row behaves like a dictionary-access values by column name
        # This allows for easier access to specified values within the database
        g.db.row_factory = sqlite3.Row
    return g.db


# Initialize database with proper variables
def init_db():
    db = get_db()
    # Had to add this to combat issues with database access
    db.execute("""
            DROP TABLE IF EXISTS device_status;
        """)
    # Changed primary key set up here in order to track history of device status
    db.execute("""
            CREATE TABLE IF NOT EXISTS device_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                time_stamp TEXT NOT NULL,
                battery_level INTEGER NOT NULL,
                rssi INTEGER NOT NULL,
                online BOOLEAN NOT NULL
            )
        """)

    db.commit()


# Close database, include if exception is passed in
def close_db(e=None):
    # Remove if there is a database connection in g
    db = g.pop("db", None)
    if db is not None:
        db.close()
