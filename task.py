# task.py
# This file defines the Task class, which represents a single task in my app.

import datetime # Need this for handling date and time stuff

class Task:
    """
    Represents a single task with its details.
    Each task object will hold info like description, note, due date/time, etc.
    """
    def __init__(self, desc, note, due_date=None, due_time=None, email=None, id=None, status=0):
        """
        Constructor for the Task class. Initializes a new task object.
        Args:
            desc (str): The description of the task (required).
            note (str): An optional note for the task.
            due_date (str, optional): The due date (YYYY-MM-DD). Defaults to None.
            due_time (str, optional): The due time (HH:MM). Defaults to None.
            email (str, optional): User's email for reminders. Defaults to None.
            id (int, optional): The task's ID from the database. Defaults to None.
            status (int, optional): 0 for Pending, 1 for Done. Defaults to 0.
        """
        self.id = id          # Task ID (usually from database)
        self.desc = desc      # Task description (the main name)
        self.note = note      # Extra notes about the task
        self.due_date = due_date # Due date as a string (YYYY-MM-DD)
        # Make sure time is None if there's no date, doesn't make sense otherwise
        self.due_time = due_time if due_date else None
        self.email = email    # Email for sending reminders
        self.status = status  # 0 = Pending, 1 = Done

    def __str__(self):
        """
        How the task object should be represented as a string.
        Used for displaying tasks in the listbox. Just shows the description.
        """
        return self.desc

    def update_details(self, desc, note, due_date=None, due_time=None, email=None):
        """
        Method to update the details of an existing task object.
        """
        self.desc = desc
        self.note = note
        self.due_date = due_date
        # Again, ensure time is None if date is None
        self.due_time = due_time if due_date else None
        self.email = email

    def set_id(self, id):
        """
        Sets the task's ID, usually after it's inserted into the database.
        """
        self.id = id

    def update_status(self):
        """
        Marks the task as done by changing its status to 1.
        """
        self.status = 1

    @property
    def due_datetime(self):
        """
        A helper property to combine date and time strings into a proper datetime object.
        Returns a datetime object if both date and time exist and are valid, otherwise None.
        Useful for time comparisons (like for reminders).
        """
        # Only proceed if both date and time strings are present
        if self.due_date and self.due_time:
            try:
                # We store date as 'YYYY-MM-DD' and time as 'HH:MM'
                # Parse the date string
                date_part = datetime.datetime.strptime(self.due_date, '%Y-%m-%d').date()
                # Parse the time string
                time_part = datetime.datetime.strptime(self.due_time, '%H:%M').time()
                # Combine them into a single datetime object
                return datetime.datetime.combine(date_part, time_part)
            except (ValueError, TypeError):
                # If parsing fails (bad format, etc.), return None
                # print(f"DEBUG: Error parsing datetime for date='{self.due_date}', time='{self.due_time}': {e}") # Optional debug
                return None
        # Return None if there's no date or no time
        return None