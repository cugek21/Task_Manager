"""
Task Manager CLI Application

This module provides a command-line interface for managing tasks
using a MySQL database backend.
It allows users to add, display, update, and delete tasks,
with all data stored persistently in a database.

Database credentials are loaded from environment variables
using .env file. All database operations use parameterized
queries for security.
"""

import os
from contextlib import contextmanager

from dotenv import load_dotenv
import mysql.connector
from mysql.connector import MySQLConnection

load_dotenv()
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASS'),
    'database': os.getenv('DB_NAME')
}


def check_python_version(required=(3, 10)):
    """
    Raises an error if the Python version is below the required version.
    
    Args:
        required (tuple): Version of required Python.

    Raises:
        RuntimeError: If current version os lower than required.    
    """
    current = os.sys.version_info
    if current[:2] < required:
        raise RuntimeError(
        f'Requires Python {required[0]}.{required[1]}+, '
        f'but found {current.major}.{current.minor}'
        )


def connect_db() -> MySQLConnection | None:
    """
    Attempts to establish a connection with the MySQL database.

    Returns:
        MySQLConnection: Connection object to the database,
        or None if connection fails.
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f'Failed to connect: {e}')
        return None


@contextmanager
def get_db_cursor():
    """
    Yields a tuple of (conn, cursor) for database operations
    and ensures both are closed after use.

    Yields:
        tuple: (conn, cursor) for interacting with the database,
        or None if connection fails.
    """
    conn = connect_db()
    if conn is None:
        print('Failed to connect to the database.')
        yield None
        return
    cursor = conn.cursor()
    try:
        yield conn, cursor
    finally:
        cursor.close()
        conn.close()


def create_table() -> None:
    """
    Creates the 'tasks' table in the database if it does not exist yet.

    Returns:
        None
    """
    with get_db_cursor() as cursor_data:
        if cursor_data is None:
            return
        conn, cursor = cursor_data

        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    ID INT AUTO_INCREMENT PRIMARY KEY,
                    Name VARCHAR(50) NOT NULL,
                    Description VARCHAR(500) NOT NULL,
                    Status ENUM(
                        'Not Started', 'Done', 'In Progress'
                        ) DEFAULT 'Not Started' NOT NULL,
                    Created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
        except Exception as e:
            print(f'Error while creating table: {e}')


def menu(menu_text: str, max_option: int) -> int:
    """
    Displays the given menu text and returns a user choice.

    Args:
        menu_text (str): The text to display for the menu.
        max_option (int): The maximum valid option number.

    Returns:
        int: The user's selected menu option.
    """
    while True:
        print(menu_text)
        choice = input(f'Select an option (1-{max_option}): ').strip()

        if choice.isdigit() and int(choice) in range(1, max_option + 1):
            return int(choice)
        print(f'Invalid choice. Enter a number between 1 and {max_option}.')


def add_task() -> None:
    """
    Prompts the user to enter a task name and description,
    and adds it to the 'tasks' table.

    Returns:
        None
    """
    with get_db_cursor() as cursor_data:
        if cursor_data is None:
            return
        conn, cursor = cursor_data

        try:
            while True:
                name = input('Enter task name: ').strip().capitalize()
                description = input(
                    'Enter task description: '
                    ).strip().capitalize()
                if 0 < len(name) <= 50 and 0 < len(description) <= 500:
                    cursor.execute(
                        "INSERT INTO tasks (Name, Description) "
                        "VALUES (%s, %s)",
                        (name, description),
                    )
                    conn.commit()
                    print(f'Task "{name}" added successfully.')
                    break
                else:
                    print(
                    'Name and description cannot be empty '
                    'and must be at most 50 and 500 characters long.'
                    )
        except Exception as e:
            print(f'Error while adding task: {e}')


def print_tasks(rows: list[tuple]) -> None:
    """
    Prints tasks in the console.

    Args:
        rows (list[tuple]): List of task records to print.

    Returns:
        None
    """
    for id_, name, description, status, date in rows:
        print(f'''
            ID: {id_} | Name: {name} | Status: {status}
            Description: {description}
            Created: {date}
            {'_' * 60}
        ''')


def get_tasks(cursor) -> list[tuple] | None:
    """
    Returns a list of all tasks from the database,
    or None if the table is empty.

    Args:
        cursor: Database cursor to execute the query.

    Returns:
        list[tuple] or None: List of task records, or None if empty.
    """
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    if not tasks:
        print('The list is empty.')
        return
    return tasks


def display_tasks() -> None:
    """
    Displays all tasks with optional filtering by status.

    Returns:
        None
    """
    filter_menu_text = (
        '\nFilter by status:\n'
        '1. Not Started\n'
        '2. Done\n'
        '3. In Progress\n'
        '4. Continue without filter\n'
    )
    with get_db_cursor() as cursor_data:
        if cursor_data is None:
            return
        conn, cursor = cursor_data

        try:
            tasks = get_tasks(cursor)
            if not tasks:
                return
            print('All tasks:')
            print_tasks(tasks)

            choice = menu(filter_menu_text, 4)
            if choice == 1:
                status = 'Not Started'
            elif choice == 2:
                status = 'Done'
            elif choice == 3:
                status = 'In Progress'
            else:
                return

            cursor.execute("SELECT * FROM tasks WHERE Status = %s", (status,))
            filtered_tasks = cursor.fetchall()
            if not filtered_tasks:
                print('The list is empty.')
                return
            print(f'Tasks with status "{status}":')
            print_tasks(filtered_tasks)
        except Exception as e:
            print(f'Error while displaying tasks: {e}')


def update_task():
    """
    Allows the user to update the status of a selected task.

    Returns:
        None
    """
    with get_db_cursor() as cursor_data:
        if cursor_data is None:
            return
        conn, cursor = cursor_data

        try:
            tasks = get_tasks(cursor)
            if not tasks:
                return
            print('All tasks:')
            print_tasks(tasks)

            existing_ids = {str(task[0]) for task in tasks}
            while True:
                selected_id = input(
                    'Enter ID of the task to update: '
                ).strip()
                if selected_id not in existing_ids:
                    print('ID not found.')
                    continue
                new_status = input(
                    'Enter new status (In Progress or Done): '
                    ).strip().title()
                if new_status not in ['In Progress', 'Done']:
                    print('Invalid choice. Enter "In Progress" or "Done".')
                    continue
                cursor.execute(
                    "UPDATE tasks SET Status = %s WHERE ID = %s", 
                    (new_status, int(selected_id))
                    )
                conn.commit()
                print(f'Task ID {selected_id} was successfully updated.')
                break
        except Exception as e:
            print(f'Error while updating: {e}')


def delete_task() -> None:
    """
    Deletes a selected task from the database by ID.

    Returns:
        None
    """
    with get_db_cursor() as cursor_data:
        if cursor_data is None:
            return
        conn, cursor = cursor_data

        try:
            tasks = get_tasks(cursor)
            if not tasks:
                return
            print('All tasks:')
            print_tasks(tasks)

            existing_ids = {str(task[0]) for task in tasks}
            while True:
                selected_id = input(
                    'Enter the ID of the task to delete: '
                    ).strip()
                if selected_id not in existing_ids:
                    print('ID not found.')
                    continue
                cursor.execute(
                    "DELETE FROM tasks WHERE ID = %s", (int(selected_id),)
                    )
                conn.commit()
                print(f'Task ID {selected_id} was successfully deleted.')
                break
        except Exception as e:
            print(f'Error while deleting: {e}')


def main() -> None:
    """
    Main loop of the program. Displays the main menu
    and reacts to user choices.

    Returns:
        None
    """
    main_menu_text = (
        '\nTask Manager - Main Menu\n'
        '1. Add Task\n'
        '2. Display Tasks\n'
        '3. Update Task\n'
        '4. Delete Task\n'
        '5. Exit Program\n'
    )
    while True:
        choice = menu(main_menu_text, 5)
        if choice == 1:
            add_task()
        elif choice == 2:
            display_tasks()
        elif choice == 3:
            update_task()
        elif choice == 4:
            delete_task()
        else:
            print('Exiting program...')
            break


if __name__ == '__main__':
    check_python_version((3,10))
    create_table()
    main()
