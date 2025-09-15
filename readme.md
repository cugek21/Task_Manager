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
    - Create your database credentials in a `.env` file in the project root. Follow example in `.env.example` file.

    - The application and tests will load these credentials automatically.
    - You can also update the `DB_CONFIG` in [src/main.py](src/main.py) and test DB config in [tests/conftest.py](tests/conftest.py) if needed.

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

Tests use a separate test database (`test_db_01`) and reset the table before each test. Test configuration and fixtures are located in `tests/conftest.py`.

## Project Structure

- `src/` - Main application code
- `tests/` - Automated tests
   - `conftest.py` - Shared test fixtures and test DB setup
   - `test_add.py` - Tests for adding tasks
   - `test_update.py` - Tests for updating tasks
   - `test_delete.py` - Tests for deleting tasks
- `requirements.txt` - Python dependencies

## Author

Radek Jíša  
radek.jisa@gmail.com