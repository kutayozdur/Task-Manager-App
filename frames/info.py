# frames/info.py
# This frame shows the details of a selected task.

import tkinter as tk
from tkinter import ttk
# Removed unused imports

class Info(ttk.Frame):
    """
    The Frame class for displaying the detailed information of a selected task.
    Shows description, note, due date/time, email, and status.
    Also contains buttons for Edit, Delete, and Mark as Done.
    """
    def __init__(self, parent, controller, show_tasks_frame, show_edit_frame):
        """
        Sets up the Info frame.
        Args:
            parent: The parent widget.
            controller: The main App class instance.
            show_tasks_frame: Function to switch back to the Tasks list.
            show_edit_frame: Function to switch to the Add/Edit frame for editing.
        """
        super().__init__(parent)

        self["style"] = "Background.TFrame" # Apply background style

        # Define fonts used in this frame
        label_font = ("Helvetica", 16) # Font for the field names (e.g., "Description:")
        value_font = ("Helvetica", 14) # Font for the actual task data

        self.controller = controller # Store reference to the main app controller

        # Back button to return to the task list
        self.back_button = ttk.Button(
            self, text="<-- Back", style="button.TButton", command=show_tasks_frame
        )
        self.back_button.grid(row=0, column=0, sticky="w", padx=20, pady=10) # Align top-left

        # Main container for the task details
        main_container = ttk.Frame(self, style="container.TFrame", padding=(20, 10))
        main_container.grid(row=1, column=0, padx=40, pady=10, sticky="nsew") # Padding around details
        main_container.columnconfigure(1, weight=1) # Allow the value column (col 1) to expand

        # --- Task Details Display ---
        row_num = 0 # Keep track of the current grid row

        # Description Label and Value
        ttk.Label(main_container, text="Description:", style="LightText_first.TLabel", font=label_font).grid(row=row_num, column=0, sticky="nw", padx=10, pady=5)
        self.task_desc_label = ttk.Label(
            main_container,
            textvariable=controller.selected_task_desc, # Linked to controller's variable
            style="LightText_second.TLabel",
            font=value_font,
            wraplength=450 # Wrap text if description is very long
        )
        self.task_desc_label.grid(row=row_num, column=1, sticky="new", padx=10, pady=5) # Expand N, E, W
        row_num += 1

        # Separator line
        ttk.Separator(main_container, orient="horizontal").grid(row=row_num, column=0, columnspan=2, sticky="ew", pady=5)
        row_num += 1

        # Note Label and Value
        ttk.Label(main_container, text="Note:", style="LightText_first.TLabel", font=label_font).grid(row=row_num, column=0, sticky="nw", padx=10, pady=5)
        self.task_note_label = ttk.Label(
            main_container,
            textvariable=controller.selected_task_note, # Linked variable
            style="LightText_second.TLabel",
            font=value_font,
            wraplength=450 # Wrap long notes
        )
        self.task_note_label.grid(row=row_num, column=1, sticky="new", padx=10, pady=5)
        row_num += 1

        # Separator line
        ttk.Separator(main_container, orient="horizontal").grid(row=row_num, column=0, columnspan=2, sticky="ew", pady=5)
        row_num += 1

        # Due Date Label and Value
        ttk.Label(main_container, text="Due Date:", style="LightText_first.TLabel", font=label_font).grid(row=row_num, column=0, sticky="nw", padx=10, pady=5)
        self.task_date_label = ttk.Label(
            main_container,
            textvariable=controller.selected_task_date_str, # Linked variable (shows "N/A" if no date)
            style="LightText_second.TLabel", font=value_font
        )
        self.task_date_label.grid(row=row_num, column=1, sticky="new", padx=10, pady=5)
        row_num += 1

        # Due Time Label and Value
        ttk.Label(main_container, text="Due Time:", style="LightText_first.TLabel", font=label_font).grid(row=row_num, column=0, sticky="nw", padx=10, pady=5)
        self.task_time_label = ttk.Label(
            main_container,
            textvariable=controller.selected_task_time_str, # Linked variable (shows "N/A" if no time)
            style="LightText_second.TLabel", font=value_font
        )
        self.task_time_label.grid(row=row_num, column=1, sticky="new", padx=10, pady=5)
        row_num += 1

        # Email Label and Value
        ttk.Label(main_container, text="Email:", style="LightText_first.TLabel", font=label_font).grid(row=row_num, column=0, sticky="nw", padx=10, pady=5)
        self.task_email_label = ttk.Label(
            main_container,
            textvariable=controller.selected_task_email_str, # Linked variable (shows "N/A" if no email)
            style="LightText_second.TLabel", font=value_font,
            wraplength=450 # Wrap long emails (less likely)
        )
        self.task_email_label.grid(row=row_num, column=1, sticky="new", padx=10, pady=5)
        row_num += 1

        # Separator line
        ttk.Separator(main_container, orient="horizontal").grid(row=row_num, column=0, columnspan=2, sticky="ew", pady=5)
        row_num += 1

        # Status Label and Value
        ttk.Label(main_container, text="Status:", style="LightText_first.TLabel", font=label_font).grid(row=row_num, column=0, sticky="nw", padx=10, pady=5)
        status_label = ttk.Label(
            main_container,
            textvariable=controller.selected_task_status_str, # Linked variable ("Pending" or "Done")
            style="LightText_second.TLabel", font=value_font
        )
        status_label.grid(row=row_num, column=1, sticky="new", padx=10, pady=5)
        row_num += 1

        # --- Buttons ---
        # Container for the action buttons (Edit, Delete, Done)
        button_container = ttk.Frame(self, padding=10, style="container.TFrame")
        button_container.grid(row=3, column=0, sticky="ew") # Below details, expand horizontally
        # Make button columns expand equally to space them out
        button_container.columnconfigure((0, 1, 2), weight=1)

        # Edit Button
        self.edit_button = ttk.Button(
            button_container, text="Edit", style="button.TButton",
            # Lambda calls controller's prep function THEN switches frame
            command=lambda: [controller.edit_task_prep(), show_edit_frame()]
        )
        self.edit_button.grid(row=0, column=0, sticky="ew", padx=5, pady=10) # Expand E-W

        # Delete Button
        delete_button = ttk.Button(
            button_container, text="Delete", style="button.TButton",
            # Calls controller method to show confirmation dialog
            command=lambda: controller.show_delete_confirmation(controller.selected_task_id.get())
        )
        delete_button.grid(row=0, column=1, sticky="ew", padx=5, pady=10) # Expand E-W

        # Mark as Done Button
        self.select_done_button = ttk.Button(
            button_container, text="Mark as Done", style="button.TButton",
            # Lambda calls controller's status change THEN updates button states here
            command=lambda: [
                controller.change_status(controller.selected_task_id.get()),
                self.update_button_states(), # Disable buttons immediately if marked done
            ]
        )
        self.select_done_button.grid(row=0, column=2, sticky="ew", padx=5, pady=10) # Expand E-W


    def update_button_states(self):
        """
        Checks the current task's status (via the controller's variable)
        and enables/disables the 'Edit' and 'Mark as Done' buttons accordingly.
        If status is 'Done', buttons are disabled. Otherwise, they are enabled.
        """
        # Check the string variable linked to the status label
        is_done = self.controller.selected_task_status_str.get() == "Done"
        # Set state based on whether the task is done
        state = "disabled" if is_done else "normal"
        try: # Added try-except in case widgets destroyed during shutdown
            self.edit_button.config(state=state)
            self.select_done_button.config(state=state)
        except tk.TclError:
            pass