import tkinter as tk
from tkinter import ttk
from frames import Tasks, AddEdit, Info
from database_manager import DatabaseManager
from datetime import date
from task import Task
from tkinter import messagebox

# Pyinstaller - Spec

# datas

# added_files = [
#     ("database_manager.py", "."),
#     ("task_database.db", "."),
#     ("task.py", "."),
#     ("frames/*.py", "frames"),
# ]

# hidden imports

# babel.numbers


COLOUR_PRIMARY = "#394867"
COLOUR_SECONDARY = "#212A3E"
COLOUR_LIGHT_BACKGROUND = "#F1F6F9"
COLOUR_LIGHT_TEXT = "#EEEEEE"
COLOUR_DARK_TEXT = "#212A3E"


class TaskManager(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("Tasks.TFrame", background=COLOUR_LIGHT_BACKGROUND)
        style.configure("Info.TFrame", background=COLOUR_LIGHT_BACKGROUND)
        style.configure("AddEdit.TFrame", background=COLOUR_LIGHT_BACKGROUND)
        style.configure("Background.TFrame", background=COLOUR_PRIMARY)

        style.configure(
            "title.TLabel",
            background=COLOUR_PRIMARY,
            foreground=COLOUR_LIGHT_TEXT,
            font="Courier 38",
        )

        style.configure(
            "LightText_first.TLabel",
            background=COLOUR_PRIMARY,
            foreground=COLOUR_LIGHT_TEXT,
            font="Helvetica 25",
        )

        style.configure(
            "LightText_second.TLabel",
            background=COLOUR_PRIMARY,
            foreground=COLOUR_LIGHT_TEXT,
            font="Helvetica 20",
        )

        style.configure(
            "button.TButton",
            background=COLOUR_SECONDARY,
            foreground=COLOUR_LIGHT_TEXT,
        )

        style.map(
            "button.TButton",
            background=[("active", COLOUR_PRIMARY)],
        )

        style.configure(
            "checkbutton.TCheckbutton",
            background=COLOUR_PRIMARY,
            foreground=COLOUR_LIGHT_TEXT,
            font="Helvetica 20",
        )
        style.map(
            "checkbutton.TCheckbutton",
            background=[("active", COLOUR_PRIMARY)],
        )

        style.configure(
            "enrty.TEntry",
            background=COLOUR_SECONDARY,
            foreground=COLOUR_LIGHT_TEXT,
        )

        style.configure("container.TFrame", background=COLOUR_PRIMARY)

        self["background"] = COLOUR_PRIMARY

        self.title("Task Manager")
        self.resizable(False, False)

        container = ttk.Frame(self)
        container.grid(row=0, column=0, sticky="nesw", padx=(20, 40))

        self.frames = dict()

        # Add or Edit label
        self.add_or_edit = tk.StringVar(value="Add Task")

        # For info frame
        self.selected_task_desc = tk.StringVar()
        self.selected_task_note = tk.StringVar()
        self.selected_task_date = tk.StringVar(value=None)
        self.selected_task_status = tk.StringVar(value="Pending")
        self.selected_task_id = tk.IntVar()

        # For date label in the info frame
        self.date_text = tk.StringVar()

        db_file = "/Users/kutayozdur/Documents/PythonProjects/task-manager-app/task_database.db"
        self.db_manager = DatabaseManager(db_file)

        tasks_frame = Tasks(
            container,
            self,
            lambda: self.show_frame(AddEdit),
            lambda: self.show_frame(Info),
        )
        tasks_frame.grid(row=0, column=0, sticky="nesw")

        add_edit_frame = AddEdit(container, self, lambda: self.show_frame(Tasks))
        add_edit_frame.grid(row=0, column=0, sticky="nsew")

        info_frame = Info(
            container,
            self,
            lambda: self.show_frame(Tasks),
            lambda: self.show_frame(AddEdit),
        )
        info_frame.grid(row=0, column=0, sticky="nsew")

        self.frames[Tasks] = tasks_frame
        self.frames[AddEdit] = add_edit_frame
        self.frames[Info] = info_frame

        # Show the tasks in the listbox
        self.fill_listbox(self.db_manager.get_all_tasks())

        # Clears the tasks table
        # self.db_manager.clear_tasks_table()

        self.show_frame(Tasks)

    def show_frame(self, container):
        frame = self.frames[container]
        frame.tkraise()

    def fill_listbox(self, task_list):
        tasks_date_list = []
        tasks_with_date_list = []
        tasks_without_date_list = []
        for task in task_list:
            if task.due_date is not None:
                tasks_with_date_list.append(task)
            else:
                tasks_without_date_list.append(task)

        # Sort tasks with due dates
        tasks_with_date_list.sort(key=lambda task: task.due_date[::-1])

        # Combine tasks with due dates and tasks without due dates
        tasks_date_list = tasks_with_date_list + tasks_without_date_list

        # Clear the listbox before filling it again
        self.frames[Tasks].tasks_listbox.delete(0, tk.END)

        # Fill the listbox with the sorted tasks
        for task in tasks_date_list:
            self.frames[Tasks].tasks_listbox.insert(tk.END, task)

    def on_double_click(self):
        listbox = self.frames[Tasks].tasks_listbox
        selected_task_index_tuple = listbox.curselection()
        selected_task_name = listbox.get(selected_task_index_tuple[0])
        selected_task = self.db_manager.get_task_by_name(selected_task_name)
        self.selected_task_desc.set(selected_task.desc)
        self.selected_task_note.set(selected_task.note)
        self.selected_task_date.set(selected_task.due_date)
        self.selected_task_id.set(selected_task.id)

        edit_button = self.frames[Info].edit_button
        select_done_button = self.frames[Info].select_done_button

        if selected_task.status == 0:
            self.selected_task_status.set("Pending")
            edit_button.config(state="normal")
            select_done_button.config(state="normal")
        elif selected_task.status == 1:
            self.selected_task_status.set("Done")
            edit_button.config(state="disabled")
            select_done_button.config(state="disabled")

    def check_date(self):
        if self.selected_task_date == None:
            return "This task has no due date."
        else:
            return self.selected_task_date

    # Changing a task's status ("Pending" to "Done")
    def change_status(self, task_id):
        self.db_manager.update_status(task_id)
        self.selected_task_status.set("Done")

    # Delete a task
    def delete_task(self, task_id):
        self.db_manager.delete_task(task_id)

    def show_messagebox(self, task_id):
        yes_or_no = messagebox.askyesno(
            title="Confirm Task Deletion",
            message="Are you sure you want to delete this task? This action cannot be undone.",
        )
        # If the user selects "yes"
        if yes_or_no:
            self.delete_task(task_id)
            task_list = self.db_manager.get_all_tasks()
            self.fill_listbox(task_list)
            self.show_frame(Tasks)
        # If the user selects "no"
        elif not yes_or_no:
            pass

    # Editing a task
    def edit_task_prep(self):
        frame = self.frames[AddEdit]
        self.add_or_edit.set("Edit Task")
        frame.task_desc.set(self.selected_task_desc.get())
        frame.task_note_input.insert("1.0", self.selected_task_note.get())

        is_null = self.db_manager.is_task_date_null(self.selected_task_id.get())

        # If selected task doesnt have a due date
        if is_null:
            frame.cal.selection_clear()
            frame.cal.selection_set(date.today())
        # If selected task does have a due date
        else:
            frame.is_checked.set(1)
            frame.disable_dates()
            frame.cal.selection_set(self.selected_task_date.get())

    def edit_task(self, desc, note, date, id):
        self.db_manager.update_task_with_date(
            desc,
            note,
            date,
            id,
        )


try:
    app = TaskManager()
    app.mainloop()
except:
    import traceback

    traceback.print_exc()
    input("Press enter to end...")
