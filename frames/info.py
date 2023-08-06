import tkinter as tk
from tkinter import ttk
from task import Task
from tkcalendar import *
from tkinter import messagebox


class Info(ttk.Frame):
    def __init__(self, parent, controller, show_tasks_frame, show_edit_frame):
        super().__init__(parent)

        self["style"] = "Background.TFrame"

        self.controller = controller

        self.back_button = ttk.Button(
            self, text="<-- Back", style="button.TButton", command=show_tasks_frame
        )
        self.back_button.grid(row=0, column=0, sticky="w", padx=20, pady=10)

        main_container = ttk.Frame(self, style="container.TFrame")
        main_container.grid(row=1, column=0, padx=40, pady=10)

        ttk.Label(
            main_container,
            text="Task description: ",
            style="LightText_first.TLabel",
        ).grid(row=0, column=0, sticky="w", padx=10, pady=20)

        self.task_desc_label = ttk.Label(
            main_container,
            textvariable=controller.selected_task_desc,
            style="LightText_second.TLabel",
        )

        self.task_desc_label.grid(row=0, column=1, sticky="ew", padx=10, pady=10)

        ttk.Separator(main_container, orient="horizontal").grid(
            row=1, column=0, sticky="ew", pady=10
        )

        ttk.Label(
            main_container,
            text="Task note: ",
            style="LightText_first.TLabel",
        ).grid(row=2, column=0, sticky="w", padx=10, pady=20)

        self.task_note_label = ttk.Label(
            main_container,
            textvariable=controller.selected_task_note,
            style="LightText_second.TLabel",
            wraplength=400,
        )

        self.task_note_label.grid(row=2, column=1, sticky="ew", padx=10, pady=10)

        ttk.Separator(main_container, orient="horizontal").grid(
            row=3, column=0, sticky="ew", pady=10
        )

        ttk.Label(
            main_container,
            text="Due date:",
            style="LightText_first.TLabel",
        ).grid(row=4, column=0, sticky="w", padx=10, pady=20)

        date_text_value = controller.check_date()
        ttk.Label(
            main_container,
            textvariable=date_text_value,
            style="LightText_second.TLabel",
        ).grid(row=4, column=1, sticky="ew", padx=10, pady=10)

        ttk.Separator(main_container, orient="horizontal").grid(
            row=5, column=0, sticky="ew", pady=10
        )

        ttk.Label(
            main_container,
            text="Status:",
            style="LightText_first.TLabel",
        ).grid(row=6, column=0, sticky="w", padx=10, pady=20)

        status_label = ttk.Label(
            main_container,
            textvariable=controller.selected_task_status,
            style="LightText_second.TLabel",
        )
        status_label.grid(row=6, column=1, sticky="ew", padx=10, pady=10)

        button_container = ttk.Frame(self, padding=20, style="container.TFrame")
        button_container.grid(row=3, column=0, sticky="ew")

        self.edit_button = ttk.Button(
            button_container,
            text="Edit",
            style="button.TButton",
            command=lambda: [controller.edit_task_prep(), show_edit_frame()],
        )
        self.edit_button.grid(row=0, column=0, sticky="w", padx=10, pady=10)

        delete_button = ttk.Button(
            button_container,
            text="Delete",
            style="button.TButton",
            command=lambda: [
                controller.show_messagebox(controller.selected_task_id.get())
            ],
        )
        delete_button.grid(row=0, column=1, sticky="w", padx=10, pady=10)

        self.select_done_button = ttk.Button(
            button_container,
            text="Task is done!",
            style="button.TButton",
            command=lambda: [
                controller.change_status(controller.selected_task_id.get()),
                self.disable_buttons(),
            ],
        )
        self.select_done_button.grid(row=0, column=2, sticky="e", padx=10, pady=10)

    def disable_buttons(self):
        if self.controller.selected_task_status.get() == "Done":
            self.edit_button.config(state="disabled")
            self.select_done_button.config(state="disabled")
