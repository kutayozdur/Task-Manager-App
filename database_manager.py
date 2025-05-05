import sqlite3 as sql
from task import Task
# Removed 'from datetime import date' as it's not directly used here now


class DatabaseManager:
    def __init__(self, db_file):
        self.connection = sql.connect(db_file, check_same_thread=False) # Added check_same_thread=False for threading
        self.create_tables()

    # Create tables if they don't exist
    def create_tables(self):
        with self.connection:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY,
                    description TEXT NOT NULL UNIQUE, -- Added UNIQUE constraint
                    note TEXT,
                    date DATE,
                    time TEXT, -- Added time column
                    email TEXT, -- Added email column
                    status INTEGER DEFAULT 0 NOT NULL
                )
                """
            )
            # Optional: Add an index for faster lookups if needed, e.g., on email or date/time
            # self.connection.execute("CREATE INDEX IF NOT EXISTS idx_task_datetime ON tasks (date, time);")

    # Insert a new task into the database
    def insert_task(self, task):
         # Ensure time is None if date is None
        task_time = task.due_time if task.due_date else None
        with self.connection:
             try: # Added try-except for UNIQUE constraint on description
                cursor = self.connection.execute(
                    """
                    INSERT INTO tasks (description, note, date, time, email)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (task.desc, task.note, task.due_date, task_time, task.email),
                )
                # Set the task ID after insertion
                task.set_id(cursor.lastrowid)
                return True # Indicate success
             except sql.IntegrityError:
                 print(f"Error: Task description '{task.desc}' already exists.")
                 return False # Indicate failure


    # Delete a task from the database based on its ID
    def delete_task(self, task_id):
        with self.connection:
            self.connection.execute(
                """
                DELETE FROM tasks WHERE id=?
                """,
                (task_id,),
            )

    # Update an existing task in the database based on its ID
    # Consolidated update methods
    def update_task(self, task_id, task_desc, task_note, task_due_date, task_due_time, task_email):
        # Ensure time is None if date is None
        actual_due_time = task_due_time if task_due_date else None
        with self.connection:
            try: # Added try-except for UNIQUE constraint on description
                self.connection.execute(
                    """
                    UPDATE tasks
                    SET description=?, note=?, date=?, time=?, email=?
                    WHERE id=?
                    """,
                    (task_desc, task_note, task_due_date, actual_due_time, task_email, task_id),
                )
                return True # Indicate success
            except sql.IntegrityError:
                 print(f"Error: Task description '{task_desc}' already exists.")
                 return False # Indicate failure


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
            # Retrieve all columns including the new ones
            cursor = self.connection.execute(
                "SELECT description, note, date, time, email, id, status FROM tasks"
            )
            # Pass the fetched row directly to the Task constructor
            tasks = [Task(*row) for row in cursor.fetchall()]
            return tasks

    # Retrieve task information based on unique task ID
    def get_task_by_id(self, task_id): # Changed from get_task_by_name for reliability
        with self.connection:
            cursor = self.connection.execute(
                "SELECT description, note, date, time, email, id, status FROM tasks WHERE id=?",
                (task_id,),
            )
            task_data = cursor.fetchone()
            if task_data:
                # If a matching task is found, create a Task object
                task = Task(*task_data)
                return task
            else:
                # If the task is not found, return None
                return None

    # Check if a specific task's date is NULL (no longer strictly needed with new logic, but kept for potential use)
    def is_task_date_null(self, task_id):
        with self.connection:
            cursor = self.connection.execute(
                "SELECT date FROM tasks WHERE id=?", (task_id,)
            )
            result = cursor.fetchone()
            return result is None or result[0] is None

    # Method to get tasks due for reminders
    def get_tasks_for_reminder(self):
        with self.connection:
            cursor = self.connection.execute(
                """
                SELECT description, note, date, time, email, id, status
                FROM tasks
                WHERE date IS NOT NULL AND time IS NOT NULL AND email IS NOT NULL AND email != '' AND status = 0
                """
            )
            tasks = [Task(*row) for row in cursor.fetchall()]
            return tasks


    def clear_tasks_table(self):
        with self.connection:
            self.connection.execute("DELETE FROM tasks")

    # Close the database connection
    def close(self):
        self.connection.close()