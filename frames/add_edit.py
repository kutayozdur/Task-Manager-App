import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import *
from datetime import date
from task import Task
from database_manager import DatabaseManager
from tkinter import font


class AddEdit(ttk.Frame):
    def __init__(self, parent, controller, show_tasks_frame):
        super().__init__(parent)

        self["style"] = "Background.TFrame"

        entry_font = font.Font(family="Rockwell", size=20)

        self.controller = controller
        self.show_tasks_frame = show_tasks_frame

        # Display or not display calendar
        self.is_checked = tk.IntVar()

        # Task attributes
        self.task_desc = tk.StringVar()

        self.is_task_desc_valid = tk.BooleanVar()

        ttk.Label(self, textvariable=controller.add_or_edit, style="title.TLabel").grid(
            row=0, column=0, sticky="w", padx=20, pady=10
        )

        main_container = ttk.Frame(self, style="container.TFrame")
        main_container.grid(row=1, column=0, sticky="nsew", padx=40, pady=10)

        ttk.Label(
            main_container,
            text="Task description: ",
            style="LightText_first.TLabel",
        ).grid(row=0, column=0, sticky="w", padx=10, pady=20)

        self.task_desc_input = ttk.Entry(
            main_container,
            textvariable=self.task_desc,
            width=50,
            background="#394867",
            font=entry_font,
        )
        self.task_desc_input.grid(
            row=0, column=1, sticky="ew", padx=10, pady=10, ipady=3
        )

        ttk.Label(
            main_container,
            text="Task Note: ",
            style="LightText_first.TLabel",
        ).grid(row=1, column=0, sticky="w", padx=10, pady=20)

        self.task_note_input = tk.Text(
            main_container,
            width=50,
            height=5,
            background="#212A3E",
            foreground="#EEEEEE",
            font=entry_font,
        )
        self.task_note_input.grid(
            row=1, column=1, sticky="ew", padx=10, pady=10, ipady=3
        )

        self.date_set_check = ttk.Checkbutton(
            main_container,
            padding=10,
            text="Set date",
            offvalue=0,
            onvalue=1,
            variable=self.is_checked,
            command=self.disable_dates,
            style="checkbutton.TCheckbutton",
        )
        self.date_set_check.grid(row=2, column=0, sticky="w", padx=10, pady=20)

        self.cal = Calendar(
            main_container,
            selectmode="none",
            mindate=date.today(),
            showweeknumbers=False,
            background="#212A3E",
            foreground="#EEEEEE",
        )
        self.cal.grid(row=2, column=1, sticky="ew", padx=30, pady=30)
        self.cal.selection_set(date.today())

        button_container = ttk.Frame(self, padding=20, style="container.TFrame")
        button_container.grid(row=3, column=0, sticky="ew", padx=10, pady=20)

        button_container.columnconfigure(0, weight=1)

        self.cancel_button = ttk.Button(
            button_container,
            text="Cancel",
            style="button.TButton",
            command=lambda: [show_tasks_frame(), self.clear_frame()],
        )
        self.cancel_button.grid(row=0, column=0, sticky="e", padx=10)

        self.done_button = ttk.Button(
            button_container,
            text="Done",
            style="button.TButton",
            command=self.create_or_edit,
        )
        self.done_button.grid(row=0, column=1, sticky="e", padx=10)

    def disable_dates(self):
        if self.is_checked.get() == 0:
            # Disable the calendar
            self.cal.config(selectmode="none")

        else:
            # Enable the calendar
            self.cal.config(selectmode="day")

    # Check if task description is valid
    def check_task_desc(self):
        # Check if task description is empty and unique
        if len(self.task_desc.get().strip()) == 0:
            messagebox.showerror(title="Error", message="Please type the task's name")
            self.is_task_desc_valid = False
        elif not self.is_desc_unique(self.task_desc.get()):
            messagebox.showerror(
                title="Error", message="This task name already used in another task"
            )
            self.is_task_desc_valid = False
        else:
            self.is_task_desc_valid = True

    # Creating tasks
    def create_task(self):
        self.check_task_desc()
        if not self.is_task_desc_valid:
            return

        if self.is_checked.get() == 1:
            new_task = Task(
                self.task_desc.get(),
                self.task_note_input.get("1.0", tk.END).strip(),
                self.cal.get_date(),
            )

        elif self.is_checked.get() == 0:
            new_task = Task(
                self.task_desc.get(),
                self.task_note_input.get("1.0", tk.END).strip(),
            )

        self.controller.db_manager.insert_task(new_task)
        task_list = self.controller.db_manager.get_all_tasks()
        self.controller.fill_listbox(task_list)

        self.show_tasks_frame()
        self.clear_frame()

    def clear_frame(self):
        self.task_desc_input.delete(0, "end")
        self.task_note_input.delete(1.0, "end")
        self.cal.selection_clear()
        self.cal.selection_set(date.today())
        self.cal.config(selectmode="none")
        self.is_checked.set(0)
        self.disable_dates()

    def is_desc_unique(self, new_desc):
        tasks = self.controller.db_manager.get_all_tasks()
        for task in tasks:
            if new_desc.strip() == task.desc.strip():
                return False
        return True

    def create_or_edit(self):
        if self.controller.add_or_edit.get() == "Add Task":
            self.create_task()
        elif self.controller.add_or_edit.get() == "Edit Task":
            if len(self.task_desc.get().strip()) == 0:
                messagebox.showerror(
                    title="Error", message="Please type the task's name"
                )
            else:
                # If there is no date value
                if self.is_checked.get() == 0:
                    self.controller.edit_task(
                        self.task_desc.get(),
                        self.task_note_input.get("1.0", tk.END).strip(),
                        None,
                        self.controller.selected_task_id.get(),
                    )
                # If there is date value
                elif self.is_checked.get() == 1:
                    self.controller.edit_task(
                        self.task_desc.get(),
                        self.task_note_input.get("1.0", tk.END).strip(),
                        self.cal.get_date(),
                        self.controller.selected_task_id.get(),
                    )

                task_list = self.controller.db_manager.get_all_tasks()
                self.controller.fill_listbox(task_list)
                self.show_tasks_frame()
                self.clear_frame()
