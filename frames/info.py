import tkinter as tk
from tkinter import ttk
# Removed Task, Calendar, messagebox imports as they aren't directly used here

class Info(ttk.Frame):
    def __init__(self, parent, controller, show_tasks_frame, show_edit_frame):
        super().__init__(parent)

        self["style"] = "Background.TFrame"
        label_font = ("Helvetica", 16) # Define font once
        value_font = ("Helvetica", 14) # Define font once

        self.controller = controller

        self.back_button = ttk.Button(
            self, text="<-- Back", style="button.TButton", command=show_tasks_frame
        )
        self.back_button.grid(row=0, column=0, sticky="w", padx=20, pady=10)

        main_container = ttk.Frame(self, style="container.TFrame", padding=(20, 10)) # Add padding
        main_container.grid(row=1, column=0, padx=40, pady=10, sticky="nsew")
        main_container.columnconfigure(1, weight=1) # Allow value column to expand

        # --- Task Details ---
        row_num = 0
        # Description
        ttk.Label(main_container, text="Description:", style="LightText_first.TLabel", font=label_font).grid(row=row_num, column=0, sticky="nw", padx=10, pady=5)
        self.task_desc_label = ttk.Label(main_container, textvariable=controller.selected_task_desc, style="LightText_second.TLabel", font=value_font, wraplength=450)
        self.task_desc_label.grid(row=row_num, column=1, sticky="new", padx=10, pady=5)
        row_num += 1

        # Separator
        ttk.Separator(main_container, orient="horizontal").grid(row=row_num, column=0, columnspan=2, sticky="ew", pady=5)
        row_num += 1

        # Note
        ttk.Label(main_container, text="Note:", style="LightText_first.TLabel", font=label_font).grid(row=row_num, column=0, sticky="nw", padx=10, pady=5)
        self.task_note_label = ttk.Label(main_container, textvariable=controller.selected_task_note, style="LightText_second.TLabel", font=value_font, wraplength=450)
        self.task_note_label.grid(row=row_num, column=1, sticky="new", padx=10, pady=5)
        row_num += 1

        # Separator
        ttk.Separator(main_container, orient="horizontal").grid(row=row_num, column=0, columnspan=2, sticky="ew", pady=5)
        row_num += 1

        # Due Date
        ttk.Label(main_container, text="Due Date:", style="LightText_first.TLabel", font=label_font).grid(row=row_num, column=0, sticky="nw", padx=10, pady=5)
        self.task_date_label = ttk.Label(main_container, textvariable=controller.selected_task_date_str, style="LightText_second.TLabel", font=value_font) # Use new StringVar
        self.task_date_label.grid(row=row_num, column=1, sticky="new", padx=10, pady=5)
        row_num += 1

        # Due Time
        ttk.Label(main_container, text="Due Time:", style="LightText_first.TLabel", font=label_font).grid(row=row_num, column=0, sticky="nw", padx=10, pady=5)
        self.task_time_label = ttk.Label(main_container, textvariable=controller.selected_task_time_str, style="LightText_second.TLabel", font=value_font) # Use new StringVar
        self.task_time_label.grid(row=row_num, column=1, sticky="new", padx=10, pady=5)
        row_num += 1

        # Email
        ttk.Label(main_container, text="Email:", style="LightText_first.TLabel", font=label_font).grid(row=row_num, column=0, sticky="nw", padx=10, pady=5)
        self.task_email_label = ttk.Label(main_container, textvariable=controller.selected_task_email_str, style="LightText_second.TLabel", font=value_font, wraplength=450) # Use new StringVar
        self.task_email_label.grid(row=row_num, column=1, sticky="new", padx=10, pady=5)
        row_num += 1


        # Separator
        ttk.Separator(main_container, orient="horizontal").grid(row=row_num, column=0, columnspan=2, sticky="ew", pady=5)
        row_num += 1

        # Status
        ttk.Label(main_container, text="Status:", style="LightText_first.TLabel", font=label_font).grid(row=row_num, column=0, sticky="nw", padx=10, pady=5)
        status_label = ttk.Label(main_container, textvariable=controller.selected_task_status_str, style="LightText_second.TLabel", font=value_font) # Use new StringVar
        status_label.grid(row=row_num, column=1, sticky="new", padx=10, pady=5)
        row_num += 1

        # --- Buttons ---
        button_container = ttk.Frame(self, padding=10, style="container.TFrame")
        button_container.grid(row=3, column=0, sticky="ew") # Adjusted row
        # Add weights to distribute buttons if needed
        button_container.columnconfigure((0, 1, 2), weight=1)


        self.edit_button = ttk.Button(
            button_container, text="Edit", style="button.TButton",
            command=lambda: [controller.edit_task_prep(), show_edit_frame()]
        )
        self.edit_button.grid(row=0, column=0, sticky="ew", padx=5, pady=10) # Use ew sticky

        delete_button = ttk.Button(
            button_container, text="Delete", style="button.TButton",
            command=lambda: controller.show_delete_confirmation(controller.selected_task_id.get()) # Use clearer method name
        )
        delete_button.grid(row=0, column=1, sticky="ew", padx=5, pady=10) # Use ew sticky

        self.select_done_button = ttk.Button(
            button_container, text="Mark as Done", style="button.TButton", # Changed text
            command=lambda: [
                controller.change_status(controller.selected_task_id.get()),
                self.update_button_states(), # Update button states after action
            ]
        )
        self.select_done_button.grid(row=0, column=2, sticky="ew", padx=5, pady=10) # Use ew sticky

    def update_button_states(self):
        """Disables Edit and Mark as Done buttons if the task status is 'Done'."""
        is_done = self.controller.selected_task_status_str.get() == "Done"
        state = "disabled" if is_done else "normal"
        self.edit_button.config(state=state)
        self.select_done_button.config(state=state)

    # disable_buttons renamed to update_button_states for clarity