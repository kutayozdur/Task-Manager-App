import datetime # Added import

class Task:
    def __init__(self, desc, note, due_date=None, due_time=None, email=None, id=None, status=0): # Added due_time and email
        self.id = id
        self.desc = desc
        self.note = note
        self.due_date = due_date
        # Ensure due_time is None if due_date is None
        self.due_time = due_time if due_date else None # Added logic
        self.email = email # Added email
        self.status = status

    def __str__(self):
        return self.desc

    def update_details(self, desc, note, due_date=None, due_time=None, email=None): # Added due_time and email
        self.desc = desc
        self.note = note
        self.due_date = due_date
        # Ensure due_time is None if due_date is None
        self.due_time = due_time if due_date else None # Added logic
        self.email = email # Added email

    def set_id(self, id):
        self.id = id

    def update_status(self):
        self.status = 1

    # Helper property to get datetime object if date and time exist
    @property
    def due_datetime(self):
        if self.due_date and self.due_time:
            try:
                # Assuming due_date is 'YYYY-MM-DD' and due_time is 'HH:MM'
                date_part = datetime.datetime.strptime(self.due_date, '%Y-%m-%d').date()
                time_part = datetime.datetime.strptime(self.due_time, '%H:%M').time()
                return datetime.datetime.combine(date_part, time_part)
            except (ValueError, TypeError):
                # Handle cases where date/time format might be incorrect or None
                return None
        return None