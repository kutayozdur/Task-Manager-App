from datetime import date
import sqlite3 as sql
from task import Task


class DatabaseManager:
    def __init__(self, db_file):
        self.connection = sql.connect(db_file)
        self.create_tables()

    # Create tables if they don't exist
    def create_tables(self):
        with self.connection:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY,
                    description TEXT NOT NULL,
                    note TEXT,
                    date DATE,
                    status INTEGER DEFAULT 0 NOT NULL,
                    reminder DATETIME
                )
                """
            )

    # Insert a new task into the database
    def insert_task(self, task):
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO tasks (description, note, date, reminder)
                 VALUES (?, ?, ?, ?)
                """,
                (task.desc, task.note, task.due_date, task.reminder),
            )

    # Delete a task from the database based on its ID
    def delete_task(self, task_id):
        with self.connection:
            self.connection.execute(
                """
                DELETE FROM tasks WHERE id=?    
                """,
                (task_id,),
            )

    # Update an existing task with a date value in the database based on its ID
    def update_task_with_date(self, task_desc, task_note, task_due_date, task_reminder, task_id):
        with self.connection:
            self.connection.execute(
                """
                UPDATE tasks
                SET description=?, note=?, date=?,reminder=?
                WHERE id=?
                """,
                (task_desc, task_note, task_due_date, task_reminder ,task_id),
            )

    # Update an existing task without a date value in the database based on its ID
    def update_task_without_date(self, task_desc, task_note, task_id):
        with self.connection:
            self.connection.execute(
                """
                UPDATE tasks
                SET description=?, note=?
                WHERE id=?
                """,
                (task_desc, task_note, task_id),
            )

    # Update an existing task's status based on its ID
    def update_status(self, task_id):
        with self.connection:
            self.connection.execute(
                """
                UPDATE tasks
                SET status=?
                WHERE id=?
                """,
                (1, task_id),
            )

    # Retrieve all tasks from the database and return them as a list of Task objects
    def get_all_tasks(self):
        with self.connection:
            cursor = self.connection.execute(
                "SELECT description, note, date, id, status FROM tasks"
            )
            tasks = [Task(*row) for row in cursor.fetchall()]
            return tasks

    # Retrieve task information based on unique task name (description)
    def get_task_by_name(self, task_name):
        with self.connection:
            cursor = self.connection.execute(
                "SELECT description, note, date, id, status FROM tasks WHERE description=?",
                (task_name,),
            )
            task_data = cursor.fetchone()
            if task_data:
                # If a matching task is found in the database, create a Task object
                task = Task(*task_data)
                return task
            else:
                # If the task is not found, return None
                return None

    # Get task id from task's desc
    def get_task_id(self, task_desc):
        with self.connection:
            cursor = self.connection.execute(
                """
                SELECT id
                FROM tasks
                WHERE description=?
                    """,
                (task_desc,),
            )
            task_id = cursor.fetchone()
            return task_id

    # Check if a specific task's date is NULL or not
    def is_task_date_null(self, task_id):
        with self.connection:
            cursor = self.connection.execute(
                "SELECT date FROM tasks WHERE id=?", (task_id,)
            )
            task_date = cursor.fetchone()[0]  # Fetch the date value from the result
            return task_date is None

    def clear_tasks_table(self):
        with self.connection:
            self.connection.execute("DELETE FROM tasks")

    # Close the database connection
    def close(self):
        self.connection.close()
