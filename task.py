class Task:
    def __init__(self, desc, note, due_date=None, id=None, status=0):
        self.id = id
        self.desc = desc
        self.note = note
        self.due_date = due_date
        self.status = status

    def __str__(self):
        return self.desc

    def update_details(self, desc, note, due_date=None):
        self.desc = desc
        self.note = note
        self.due_date = due_date

    def set_id(self, id):
        self.id = id

    def update_status(self):
        self.status = 1
