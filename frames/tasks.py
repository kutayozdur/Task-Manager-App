import tkinter as tk
from tkinter import ttk
from tkinter import font


class Tasks(ttk.Frame):
    def __init__(self, parent, controller, show_add_frame, show_info_frame):
        super().__init__(parent)

        listbox_font = font.Font(family="Rockwell", size=20)

        self["style"] = "Background.TFrame"

        self.controller = controller

        task_manager_label = ttk.Label(
            self,
            text="Task Manager",
            style="title.TLabel",
        )
        task_manager_label.grid(row=0, column=0, sticky="w", padx=20, pady=20)

        tasks_frame = ttk.Frame(self, height="100")
        tasks_frame.grid(row=1, column=0, sticky="nsew", padx=60, pady=10)

        scrollbar = tk.Scrollbar(
            tasks_frame,
            orient="vertical",
        )

        self.tasks_listbox = tk.Listbox(
            tasks_frame,
            width="50",
            yscrollcommand=scrollbar.set,
            font=listbox_font,
            background="#212A3E",
            foreground="#fff",
            activestyle="none",
            height=15,
        )
        self.tasks_listbox.grid(row=0, column=0, sticky="nsew")

        scrollbar.config(command=self.tasks_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")

        buttons_container = ttk.Frame(self, style="container.TFrame")
        buttons_container.grid(row=2, column=0, sticky="ew")

        buttons_container.columnconfigure((0, 1), weight=1)
        buttons_container.rowconfigure(0, weight=1)


        self.add_button = ttk.Button(
            buttons_container,
            text="Add",
            style="button.TButton",
            command=lambda: [self.change_label_to_add(), show_add_frame()],
        )
        self.add_button.grid(row=0, column=0, sticky="ew", padx=20, pady=20)

        self.exit_button = ttk.Button(
            buttons_container,
            text="Exit",
            style="button.TButton",
            command=lambda: self.controller.destroy(),
        )
        self.exit_button.grid(row=0, column=1, sticky="ew", padx=20, pady=20)

        self.tasks_listbox.bind(
            "<Double-1>",
            lambda event: [controller.on_double_click(), show_info_frame()],
        )

    def change_label_to_add(self):
        self.controller.add_or_edit.set("Add Task")
