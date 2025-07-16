# Task Manager

A simple command-line Task Manager application using Python and MySQL. Includes automated tests with pytest.

## Features

- Add, display, update, and delete tasks stored in a MySQL database
- Task status management (`Not Started`, `In Progress`, `Done`)
- Input validation for task name and description
- Automated tests for all core functionality

## Requirements

- Python 3.10+
- MySQL server running locally
- The following Python packages (see [requirements.txt](requirements.txt)):
  - mysql-connector-python
  - pytest

## Setup

1. **Install dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

2. **Configure MySQL:**

   - Ensure MySQL is running and accessible.
   - Update the `DB_CONFIG` in [src/main.py](src/main.py) and `TEST_DB_CONFIG` in [tests/test_main.py](tests/test_main.py) with your credentials if needed.

3. **Create the database:**

   - Create `db_01` and `test_db_01` databases in MySQL before running the app and tests.

## Usage

Run the Task Manager:

```sh
python src/main.py
```

Follow the prompts to manage your tasks.

## Testing

Run all tests with pytest:

```sh
pytest
```

Tests use a separate test database (`test_db_01`) and reset the table before each test.

## Project Structure

- `src/` - Main application code
- `tests/` - Automated tests
- `requirements.txt` - Python dependencies

## Author

Radek Jíša  
radek.jisa@gmail.com