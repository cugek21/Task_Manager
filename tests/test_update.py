"""
Unit tests for updating tasks in the Task Manager application.
These tests verify updating task status, handling invalid input,
and output messages.
"""

import pytest

from src.main import get_db_cursor, add_task, update_task


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
def test_update_task_positive(
    monkeypatch: pytest.MonkeyPatch,
    id_: str,
    status: str,
    expected: str
) -> None:
    """
    Tests successful update of task status with different casing
    and spacing.

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
    monkeypatch: pytest.MonkeyPatch,
    id_1: str,
    status_1: str,
    id_2: str,
    status_2: str,
    expected: str
) -> None:
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
def test_update_task_output(
    monkeypatch: pytest.MonkeyPatch,
    id_: str,
    status: str,
    expected: str
) -> None:
    """
    Tests output messages during status update, both errors
    and success.

    Args:
        monkeypatch:
            Pytest fixture to simulate user input and capture print.
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


def test_update_task_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Tests update when there are no tasks in the database.

    Args:
        monkeypatch:
            Pytest fixture to simulate user input and capture output.

    Returns:
        None
    """
    monkeypatch.setattr('builtins.input', lambda _: '')
    printed = []
    monkeypatch.setattr('builtins.print', printed.append)

    update_task()
    expected = 'The list is empty.'
    assert any(expected in line for line in printed)
