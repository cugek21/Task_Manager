"""
Shared fixtures and test DB setup for Task Manager tests.
"""

import os

from dotenv import load_dotenv
import mysql.connector
from mysql.connector import MySQLConnection
import pytest

load_dotenv()
TEST_DB_CONFIG = {
    'host': os.getenv('TEST_DB_HOST'),
    'user': os.getenv('TEST_DB_USER'),
    'password': os.getenv('TEST_DB_PASS'),
    'database': os.getenv('TEST_DB_NAME')
    }


def connect_test_db() -> MySQLConnection | None:
    """
    Attempts to establish a connection with the test MySQL database.

    Returns:
        MySQLConnection: Connection object to the database,
        or None if connection fails.
    """
    try:
        return mysql.connector.connect(**TEST_DB_CONFIG)
    except Exception as e:
        print(f'Failed to connect: {e}')
        return None


@pytest.fixture(autouse=True)
def patch_connect_db(monkeypatch):
    """
    Automatically patches the original database connection
    function to use the test database.

    Args:
        monkeypatch: Pytest fixture for patching.

    Returns:
        None
    """
    import src.main as main
    monkeypatch.setattr(main, 'connect_db', connect_test_db)


@pytest.fixture(autouse=True)
def reset_test_table():
    """
    Resets the tasks table in the test database
    before each test by dropping and recreating it.

    Returns:
        None
    """
    conn = connect_test_db()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS tasks")
    cursor.execute("""
        CREATE TABLE tasks (
            ID INT AUTO_INCREMENT PRIMARY KEY,
            Name VARCHAR(50) NOT NULL,
            Description VARCHAR(500) NOT NULL,
            Status ENUM('Not Started', 'Done', 'In Progress') 
                DEFAULT 'Not Started' NOT NULL,
            Created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()
