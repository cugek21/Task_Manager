"""
test_main.py: Project 5 - Tester with Python

author: Radek Jíša
email: radek.jisa@gmail.com
"""

import mysql.connector
from mysql.connector import MySQLConnection
import pytest
from src.main import get_db_cursor, add_task, update_task, delete_task

TEST_DB_CONFIG = {
    'host': 'localhost', #FILL IN
    'user': 'root',
    'password': 'fahgaq3byp',
    'database': 'test_db_01'
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


@pytest.mark.parametrize(
    'invalid_name, invalid_description, valid_name, valid_description',
    [
        ('', 'walk ducks', 'Pet time', 'Walk ducks'),
        ('pet time', '', 'Pet time', 'Walk ducks'),
        ('a'*50, 'd'*501, 'A'*50, 'D'*500),
        ('a'*51, 'd'*500, 'A'*50, 'D'*500),
    ]
)
def test_add_task_negative(
                    monkeypatch,
                    invalid_name: str,
                    invalid_description: str,
                    valid_name: str,
                    valid_description: str
                    ):
    """
    Tests that invalid task inputs are rejected,
    and valid ones are accepted on retry.

    Args:
        monkeypatch: Pytest fixture to simulate user input.
        invalid_name (str): Faulty task name.
        invalid_description (str): Faulty task description.
        valid_name (str): Valid task name.
        valid_description (str): Valid task description.

    Returns:
        None
    """
    inputs = iter(
        [invalid_name, invalid_description, valid_name, valid_description]
        )
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    add_task()
    with get_db_cursor() as cursor_data:
        conn, cursor = cursor_data
        cursor.execute("SELECT COUNT(*) FROM tasks")
        result = cursor.fetchone()[0]
    assert result == 1

@pytest.mark.parametrize(
    'valid_name, valid_description, expected',
    [
        ('pet tIme', 'walk duCks', [('Pet time', 'Walk ducks')]),
        ('  pet time ', '  walk ducks ', [('Pet time', 'Walk ducks')]),
        ('a'*50, 'd'*500, [('A'+'a'*49, 'D'+'d'*499)]),
        ('tásk #1%&!', 'vřýň,.?', [('Tásk #1%&!', 'Vřýň,.?')]),
        ('DROP TABLE IF EXISTS tasks', 'attack?',
         [('Drop table if exists tasks', 'Attack?')]
         )
    ]
)
def test_add_task_positive(
    monkeypatch, valid_name: str, valid_description: str, expected: list[tuple]
    ):
    """
    Tests that valid inputs are correctly inserted into the tasks table.

    Args:
        monkeypatch: Pytest fixture to simulate user input.
        test_name (str): Task name provided by the user.
        test_description (str): Task description provided by the user.
        expected (list[tuple]): Expected result after insertion.

    Returns:
        None
    """
    inputs = iter([valid_name, valid_description])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    add_task()
    with get_db_cursor() as cursor_data:
        conn, cursor = cursor_data
        cursor.execute("SELECT Name, Description FROM tasks")
        result = cursor.fetchall()
    assert result == expected

@pytest.mark.parametrize(
    'valid_name, valid_description, expected',
    [
        ('Pet time', 'Walk ducks', 'Task "Pet time" added successfully.'),
        ('', 'd'*501,
         'Name and description cannot be empty '
         'and must be at most 50 and 500 characters long.'
         )
    ]
)
def test_add_task_output(monkeypatch, valid_name: str, valid_description: str, expected: str):
    """
    Tests the printed output after adding a task.

    Args:
        monkeypatch: Pytest fixture to simulate user input and capture output.
        test_name (str): Task name to simulate.
        test_description (str): Task description to simulate.
        expected (str): Expected printed message.

    Returns:
        None
    """
    inputs = iter([valid_name, valid_description, 'Pet time', 'Walk ducks'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    printed = []
    monkeypatch.setattr('builtins.print', printed.append)

    add_task()
    assert any(expected in line for line in printed)

@pytest.mark.parametrize(
    'id_, status, expected',
    [
        ('1', 'done', 'Done'),
        ('1', 'in progress', 'In Progress'),
        ('1', 'DONE', 'Done'),
        ('1', 'DoNe', 'Done'),
        ('  1 ', ' in progress ', 'In Progress')
    ]
)
def test_update_task_positive(monkeypatch, id_: str, status: str, expected: str):
    """
    Tests successful update of task status with different casing and spacing.

    Args:
        monkeypatch: Pytest fixture to simulate user input.
        id_ (str): ID of the task to update.
        status (str): New status to set.
        expected (str): Expected status stored in the database.

    Returns:
        None
    """
    inputs = iter(['Pet time', 'Walk ducks', id_, status])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    add_task()
    update_task()
    with get_db_cursor() as cursor_data:
        conn, cursor = cursor_data
        cursor.execute("SELECT Status FROM tasks")
        result = cursor.fetchone()
    assert result[0] == expected

@pytest.mark.parametrize(
    'id_1, status_1, id_2, status_2, expected',
    [
        ('1', 'done', '1', 'done', 'Done'),
        ('1', 'in progress', '1', 'in progress', 'In Progress')
    ]
)
def test_update_task_multiple(
    monkeypatch, id_1: str, status_1: str, id_2: str, status_2: str, expected: str
    ):
    """
    Tests multiple consecutive updates on the same task.

    Args:
        monkeypatch: Pytest fixture to simulate user input.
        id_1 (str): First update task ID.
        status_1 (str): First update status.
        id_2 (str): Second update task ID.
        status_2 (str): Second update status.
        expected (str): Final expected status.

    Returns:
        None
    """
    inputs = iter(['Pet time', 'Walk ducks', id_1, status_1, id_2, status_2])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    add_task()
    update_task()
    update_task()
    with get_db_cursor() as cursor_data:
        conn, cursor = cursor_data
        cursor.execute("SELECT Status FROM tasks")
        result = cursor.fetchone()
    assert result[0] == expected

@pytest.mark.parametrize(
    'id_, status, expected',
    [
        ('0', '', 'ID not found.'),
        ('2', '', 'ID not found.'),
        ('one', '', 'ID not found.'),
        ('', '', 'ID not found.'),
        ('DROP TABLE IF EXISTS tasks', '', 'ID not found.'),
        ('1', ' ', 'Invalid choice. Enter "In Progress" or "Done".'),
        ('1', 'Not Started',
         'Invalid choice. Enter "In Progress" or "Done".'),
        ('1', 'DROP TABLE IF EXISTS tasks',
         'Invalid choice. Enter "In Progress" or "Done".'),
        ('1', 'Done', 'Task ID 1 was successfully updated.'),
        ('1', 'in progress', 'Task ID 1 was successfully updated.')
    ]
)
def test_update_task_output(monkeypatch, id_: str, status: str, expected: str):
    """
    Tests output messages during status update, both errors and success.

    Args:
        monkeypatch: Pytest fixture to simulate user input and capture print.
        id_ (str): Task ID input.
        status (str): Status input.
        expected (str): Expected output message.

    Returns:
        None
    """
    inputs = iter(['Pet time', 'Walk ducks', id_, status])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    printed = []
    monkeypatch.setattr('builtins.print', printed.append)

    add_task()
    update_task()
    assert any(expected in line for line in printed)

def test_update_task_empty(monkeypatch):
    """
    Tests update when there are no tasks in the database.

    Args:
        monkeypatch: Pytest fixture to simulate user input and capture output.

    Returns:
        None
    """
    monkeypatch.setattr('builtins.input', lambda _: '')
    printed = []
    monkeypatch.setattr('builtins.print', printed.append)

    update_task()
    expected = 'The list is empty.'
    assert any(expected in line for line in printed)

@pytest.mark.parametrize('id_', ['1', '  1 '])
def test_delete_task_positive(monkeypatch, id_: str):
    """
    Tests that a task is successfully deleted by valid ID.

    Args:
        monkeypatch: Pytest fixture to simulate user input.
        id_ (str): Task ID to delete.

    Returns:
        None
    """
    inputs = iter(['Pet time', 'Walk ducks', id_])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    add_task()
    delete_task()
    with get_db_cursor() as cursor_data:
        conn, cursor = cursor_data
        cursor.execute(
            "SELECT * FROM tasks WHERE ID = %s", (int(id_.strip()),)
        )
        result = cursor.fetchone()
    assert result is None

@pytest.mark.parametrize(
    'id_, expected',
    [
        ('0', 'ID not found.'),
        ('2', 'ID not found.'),
        ('one', 'ID not found.'),
        ('', 'ID not found.'),
        ('DROP TABLE IF EXISTS tasks', 'ID not found.'),
        ('1', 'Task ID 1 was successfully deleted.')
    ]
)
def test_delete_task_output(monkeypatch, id_: str, expected: str):
    """
    Tests printed output when deleting a task, including invalid
    and valid cases.

    Args:
        monkeypatch: Pytest fixture to simulate user input and capture print.
        id_ (str): Task ID input.
        expected (str): Expected output message.

    Returns:
        None
    """
    if expected == 'ID not found.':
        inputs = iter(['Pet time', 'Walk ducks', id_, '1'])
    else:
        inputs = iter(['Pet time', 'Walk ducks', id_])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    printed = []
    monkeypatch.setattr('builtins.print', printed.append)

    add_task()
    delete_task()
    assert any(expected in line for line in printed)

def test_delete_task_empty(monkeypatch):
    """
    Tests delete_task when the table is empty.

    Args:
        monkeypatch: Pytest fixture to capture printed output.

    Returns:
        None
    """
    monkeypatch.setattr('builtins.input', lambda _: '')
    printed = []
    monkeypatch.setattr('builtins.print', printed.append)

    delete_task()
    expected = 'The list is empty.'
    assert any(expected in line for line in printed)
