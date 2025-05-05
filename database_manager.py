# database_manager.py
# Handles all the interactions with the SQLite database for tasks.

import sqlite3 as sql
from task import Task # Need the Task class definition

class DatabaseManager:
    """
    Manages the connection and operations for the task database.
    Includes methods to create tables, insert, update, delete, and query tasks.
    """
    def __init__(self, db_file):
        """
        Initializes the DatabaseManager.
        Connects to the specified SQLite database file.
        Args:
            db_file (str): The path to the SQLite database file.
        """
        # Connect to the SQLite database file.
        # check_same_thread=False is needed because the reminder thread will access the DB too.
        self.connection = sql.connect(db_file, check_same_thread=False)
        # Make sure the necessary table exists when the manager is created.
        self.create_tables()

    def create_tables(self):
        """
        Creates the 'tasks' table in the database if it doesn't already exist.
        Defines the columns for task details.
        """
        # Use 'with self.connection' to automatically handle transactions (commit/rollback).
        with self.connection:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY,                  -- Auto-incrementing ID
                    description TEXT NOT NULL UNIQUE,        -- Task name, must be unique
                    note TEXT,                               -- Optional notes
                    date DATE,                               -- Due date (YYYY-MM-DD)
                    time TEXT,                               -- Due time (HH:MM)
                    email TEXT,                              -- User's email
                    status INTEGER DEFAULT 0 NOT NULL        -- 0=Pending, 1=Done
                )
                """
            )
            # We could add indexes here later if performance becomes an issue.
            # Example: self.connection.execute("CREATE INDEX IF NOT EXISTS idx_task_datetime ON tasks (date, time);")

    def insert_task(self, task):
        """
        Inserts a new task (from a Task object) into the database.
        Args:
            task (Task): The Task object containing the data to insert.
        Returns:
            bool: True if insertion was successful, False otherwise (e.g., duplicate description).
        """
        # Ensure time is None if date is None before inserting.
        task_time = task.due_time if task.due_date else None
        with self.connection:
             try:
                cursor = self.connection.execute(
                    """
                    INSERT INTO tasks (description, note, date, time, email)
                    VALUES (?, ?, ?, ?, ?) -- Use placeholders to prevent SQL injection
                    """,
                    # Provide the values from the task object in the correct order
                    (task.desc, task.note, task.due_date, task_time, task.email),
                )
                # After inserting, get the automatically generated ID and set it on the task object.
                task.set_id(cursor.lastrowid)
                return True # Success!
             except sql.IntegrityError:
                 # This happens if the description isn't unique (due to UNIQUE constraint).
                 print(f"Database Error: Task description '{task.desc}' already exists.")
                 return False # Failed.

    def delete_task(self, task_id):
        """
        Deletes a task from the database based on its ID.
        Args:
            task_id (int): The ID of the task to delete.
        """
        with self.connection:
            self.connection.execute(
                """
                DELETE FROM tasks WHERE id=?
                """,
                (task_id,), # Pass task_id as a tuple
            )

    def update_task(self, task_id, task_desc, task_note, task_due_date, task_due_time, task_email):
        """
        Updates an existing task in the database based on its ID.
        Args:
            task_id (int): The ID of the task to update.
            task_desc (str): The new description.
            task_note (str): The new note.
            task_due_date (str or None): The new due date (YYYY-MM-DD).
            task_due_time (str or None): The new due time (HH:MM).
            task_email (str or None): The new email.
        Returns:
            bool: True if update was successful, False otherwise (e.g., duplicate description).
        """
        # Ensure time is None if date is None before updating.
        actual_due_time = task_due_time if task_due_date else None
        with self.connection:
            try:
                self.connection.execute(
                    """
                    UPDATE tasks
                    SET description=?, note=?, date=?, time=?, email=? -- Columns to update
                    WHERE id=? -- Condition to find the right task
                    """,
                    (task_desc, task_note, task_due_date, actual_due_time, task_email, task_id),
                )
                return True # Success!
            except sql.IntegrityError:
                 print(f"Database Error: Task description '{task_desc}' already exists.")
                 return False # Failed.

    def update_status(self, task_id):
        """
        Updates a task's status to 'Done' (1).
        Args:
            task_id (int): The ID of the task to mark as done.
        """
        with self.connection:
            self.connection.execute(
                """
                UPDATE tasks
                SET status=? -- Set status to 1 (Done)
                WHERE id=?
                """,
                (1, task_id), # Pass 1 for status, then the task_id
            )

    def get_all_tasks(self):
        """
        Retrieves all tasks from the database.
        Returns:
            list[Task]: A list of Task objects representing all tasks found.
        """
        with self.connection:
            # Select all the columns needed to reconstruct a Task object
            cursor = self.connection.execute(
                "SELECT description, note, date, time, email, id, status FROM tasks"
            )
            # Use a list comprehension to create a Task object for each row fetched.
            # The '*' unpacks the row tuple into arguments for the Task constructor.
            tasks = [Task(*row) for row in cursor.fetchall()]
            return tasks

    def get_task_by_id(self, task_id):
        """
        Retrieves a single task from the database based on its unique ID.
        Args:
            task_id (int): The ID of the task to retrieve.
        Returns:
            Task or None: The Task object if found, otherwise None.
        """
        with self.connection:
            cursor = self.connection.execute(
                # Select all necessary columns
                "SELECT description, note, date, time, email, id, status FROM tasks WHERE id=?",
                (task_id,), # Pass ID as a tuple
            )
            task_data = cursor.fetchone() # Get the first (and only) result row
            if task_data:
                # If data was found, create a Task object from it
                task = Task(*task_data)
                return task
            else:
                # If no task with that ID was found
                return None

    def is_task_date_null(self, task_id):
        """
        Checks if a specific task's date column is NULL in the database.
        (Note: Might not be strictly needed anymore with current logic, but kept just in case).
        Args:
            task_id (int): The ID of the task to check.
        Returns:
            bool: True if the date is NULL, False otherwise.
        """
        with self.connection:
            cursor = self.connection.execute(
                "SELECT date FROM tasks WHERE id=?", (task_id,)
            )
            result = cursor.fetchone()
            # Check if fetchone returned None (no task) or if the first column (date) is None
            return result is None or result[0] is None

    def get_tasks_for_reminder(self):
        """
        Retrieves tasks that are candidates for email reminders.
        Conditions: Date, Time, and Email must not be NULL or empty, and Status must be 0 (Pending).
        Returns:
            list[Task]: A list of Task objects eligible for reminders.
        """
        with self.connection:
            cursor = self.connection.execute(
                """
                SELECT description, note, date, time, email, id, status
                FROM tasks
                WHERE date IS NOT NULL AND time IS NOT NULL -- Must have date and time
                      AND email IS NOT NULL AND email != '' -- Must have a non-empty email
                      AND status = 0 -- Must be pending (not done)
                """
            )
            # Create Task objects from the results
            tasks = [Task(*row) for row in cursor.fetchall()]
            return tasks

    def clear_tasks_table(self):
        """
        Deletes ALL rows from the tasks table. Use with caution!
        Good for resetting the database during development.
        """
        with self.connection:
            self.connection.execute("DELETE FROM tasks")

    def close(self):
        """
        Closes the database connection. Should be called when the app exits.
        """
        if self.connection:
            self.connection.close()
            print("Database connection closed.") # Confirmation message