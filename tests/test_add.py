"""
Unit tests for adding tasks in the Task Manager application.

These tests verify input validation, correct insertion, and output
messages when adding tasks to the database.
"""

import pytest

from src.main import get_db_cursor, add_task


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
    monkeypatch: pytest.MonkeyPatch,
    invalid_name: str,
    invalid_description: str,
    valid_name: str,
    valid_description: str
) -> None:
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
    monkeypatch: pytest.MonkeyPatch,
    valid_name: str,
    valid_description: str,
    expected: list[tuple]
) -> None:
    """
    Tests that valid inputs are correctly inserted into tasks table.

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
def test_add_task_output(
    monkeypatch: pytest.MonkeyPatch,
    valid_name: str,
    valid_description: str,
    expected: str
) -> None:
    """
    Tests the printed output after adding a task.

    Args:
        monkeypatch:
            Pytest fixture to simulate user input and capture output.
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
