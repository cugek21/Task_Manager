"""
    Unit tests for deleting tasks in the Task Manager application.

    These tests verify correct deletion, error handling, and output messages.

    Author: Radek Jíša
    Email: radek.jisa@gmail.com
"""


import pytest

from src.main import get_db_cursor, add_task, delete_task


@pytest.mark.parametrize('id_', ['1', '  1 '])
def test_delete_task_positive(
    monkeypatch: pytest.MonkeyPatch,
    id_: str
) -> None:
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
def test_delete_task_output(
    monkeypatch: pytest.MonkeyPatch,
    id_: str,
    expected: str
) -> None:
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


def test_delete_task_empty(monkeypatch: pytest.MonkeyPatch) -> None:
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
