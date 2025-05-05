# frames/add_edit.py
# This frame is used for both adding a new task and editing an existing one.

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import Calendar # Using tkcalendar for the date picker
from datetime import date, datetime # Need date/datetime for calendar and formatting
import re # Using regex for basic email validation
from task import Task # Need the Task class
from tkinter import font # For setting custom fonts

class AddEdit(ttk.Frame):
    """
    The Frame class for the Add/Edit screen. Contains input fields
    for task details (description, note, date, time, email).
    """
    def __init__(self, parent, controller, show_tasks_frame):
        """
        Sets up the Add/Edit frame.
        Args:
            parent: The parent widget (usually the main container).
            controller: The main App class instance (to access shared data/methods like db_manager).
            show_tasks_frame: A function to call to switch back to the main Tasks frame.
        """
        super().__init__(parent)

        self["style"] = "Background.TFrame" # Apply background style

        # Define fonts we'll use in this frame
        entry_font = font.Font(family="Rockwell", size=16)
        label_font = font.Font(family="Helvetica", size=14)
        spinbox_font = font.Font(family="Rockwell", size=18) # Made spinboxes bigger

        self.controller = controller # Store reference to the main app controller
        self.show_tasks_frame = show_tasks_frame # Store function to switch frames

        # --- Validation Setup ---
        # We need to register the validation function so Tkinter can call it.
        # This makes sure users can only type valid numbers in the spinboxes.
        self.validate_hour_cmd = self.register(self.validate_spinbox_input)
        self.validate_minute_cmd = self.register(self.validate_spinbox_input)

        # --- Tkinter Variables ---
        # These variables link the input fields to Python variables.
        self.task_desc = tk.StringVar()     # For task description entry
        self.task_email = tk.StringVar()    # For email entry
        self.is_date_checked = tk.IntVar()  # Tracks if 'Set date' checkbox is checked (0 or 1)
        self.is_time_checked = tk.IntVar()  # Tracks if 'Set time' checkbox is checked (0 or 1)
        self.hour_var = tk.StringVar(value="00")   # Variable for the hour spinbox
        self.minute_var = tk.StringVar(value="00") # Variable for the minute spinbox

        # --- Widgets ---

        # Title Label (changes between "Add Task" and "Edit Task")
        ttk.Label(self, textvariable=controller.add_or_edit, style="title.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", padx=20, pady=10
        )

        # Main container for input fields
        main_container = ttk.Frame(self, style="container.TFrame")
        main_container.grid(row=1, column=0, sticky="nsew", padx=40, pady=10)
        main_container.columnconfigure(1, weight=1) # Allow the input column to expand

        # Description Label and Entry field
        ttk.Label(
            main_container, text="*Description:", style="LightText_first.TLabel", font=label_font
        ).grid(row=0, column=0, sticky="w", padx=10, pady=10) # Use sticky 'w' for left alignment
        self.task_desc_input = ttk.Entry(
            main_container, textvariable=self.task_desc, width=40, font=entry_font
        )
        self.task_desc_input.grid(row=0, column=1, sticky="ew", padx=10, pady=5) # Use sticky 'ew' to expand horizontally

        # Note Label and Text field (multi-line input)
        ttk.Label(
            main_container, text="Note:", style="LightText_first.TLabel", font=label_font
        ).grid(row=1, column=0, sticky="nw", padx=10, pady=10) # Use 'nw' to align top-left
        self.task_note_input = tk.Text(
            main_container, width=40, height=4, font=entry_font,
            background="#212A3E", foreground="#EEEEEE", insertbackground="#EEEEEE" # Custom colors
        )
        self.task_note_input.grid(row=1, column=1, sticky="ew", padx=10, pady=5)

        # --- Date & Time Section ---
        # Container for date/time widgets to group them
        datetime_frame = ttk.Frame(main_container, style="container.TFrame")
        datetime_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        datetime_frame.columnconfigure(1, weight=1) # Allow calendar column to take space

        # Checkbutton to enable/disable date setting
        self.date_set_check = ttk.Checkbutton(
            datetime_frame, padding=5, text="Set date", variable=self.is_date_checked,
            command=self.toggle_date_time_widgets, # Calls function when checked/unchecked
            style="checkbutton.TCheckbutton"
        )
        self.date_set_check.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        # Calendar widget from tkcalendar library
        self.cal = Calendar(
            datetime_frame, selectmode="day", mindate=date.today(), showweeknumbers=False,
            disableddaybackground="grey", disableddayforeground="darkgrey", # Styles for disabled state
            state='disabled' # Start disabled until 'Set date' is checked
        )
        self.cal.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        try:
            self.cal.selection_set(date.today()) # Try to pre-select today's date
        except: pass # Ignore error if today is before mindate (shouldn't happen)

        # Checkbutton to enable/disable time setting
        self.time_set_check = ttk.Checkbutton(
            datetime_frame, padding=5, text="Set time", variable=self.is_time_checked,
            command=self.toggle_time_widgets, # Calls function when checked/unchecked
            style="checkbutton.TCheckbutton", state='disabled' # Start disabled
        )
        self.time_set_check.grid(row=0, column=2, sticky="w", padx=(20, 5), pady=5)

        # Frame to hold the hour and minute spinboxes together
        time_spinbox_frame = ttk.Frame(datetime_frame, style="container.TFrame")
        time_spinbox_frame.grid(row=1, column=2, sticky="w", padx=(20, 10), pady=5)

        # Hour Spinbox (0-23)
        self.hour_spinbox = ttk.Spinbox(
            time_spinbox_frame, from_=0, to=23, wrap=True, width=3, state='disabled',
            textvariable=self.hour_var, format="%02.0f", # Ensures 2 digits (e.g., 01, 02)
            font=spinbox_font,
            validate='key', # Validate on key press
            validatecommand=(self.validate_hour_cmd, '%P', '%W') # Use registered validation command
        )
        self.hour_spinbox.grid(row=0, column=0, padx=(0,2), pady=2)
        self.hour_spinbox.widget_name = "hour" # Add name for validation function to identify

        # Simple Label for the colon ":" separator
        ttk.Label(time_spinbox_frame, text=":", style="LightText_first.TLabel", font=spinbox_font).grid(row=0, column=1, padx=0, pady=2)

        # Minute Spinbox (0-59)
        self.minute_spinbox = ttk.Spinbox(
            time_spinbox_frame, from_=0, to=59, wrap=True, width=3, state='disabled',
            textvariable=self.minute_var, format="%02.0f",
            font=spinbox_font,
            validate='key',
            validatecommand=(self.validate_minute_cmd, '%P', '%W')
        )
        self.minute_spinbox.grid(row=0, column=2, padx=(2,0), pady=2)
        self.minute_spinbox.widget_name = "minute" # Add name for validation

        # --- Email Section ---
        # Label and Entry for the reminder email
        ttk.Label(
            main_container, text="Email (for reminder):", style="LightText_first.TLabel", font=label_font
        ).grid(row=3, column=0, sticky="w", padx=10, pady=10)
        self.task_email_input = ttk.Entry(
            main_container, textvariable=self.task_email, width=40, font=entry_font
        )
        self.task_email_input.grid(row=3, column=1, sticky="ew", padx=10, pady=5)

        # --- Buttons ---
        # Container for Cancel and Save buttons
        button_container = ttk.Frame(self, padding=10, style="container.TFrame")
        button_container.grid(row=4, column=0, sticky="ew", padx=10, pady=10)
        button_container.columnconfigure((0, 1), weight=1) # Allow buttons to potentially space out

        # Cancel Button
        self.cancel_button = ttk.Button(
            button_container, text="Cancel", style="button.TButton",
            # Lambda calls two functions: switch frame AND clear inputs
            command=lambda: [show_tasks_frame(), self.clear_frame()]
        )
        self.cancel_button.grid(row=0, column=0, sticky="e", padx=10) # Align right

        # Save/Done Button
        self.done_button = ttk.Button(
            button_container, text="Save Task", style="button.TButton",
            command=self.save_task # Calls the save method
        )
        self.done_button.grid(row=0, column=1, sticky="e", padx=10) # Align right

        # Set initial state of date/time widgets when frame is first created
        self.toggle_date_time_widgets()


    def validate_spinbox_input(self, P, W):
        """
        Validation function for the hour and minute spinboxes.
        Called automatically by Tkinter when validate='key'.
        Ensures only numbers within the correct range (0-23 or 0-59)
        and with max 2 digits are typed.
        Args:
            P (str): The potential value of the entry if the change is allowed.
            W (str): The internal Tkinter name of the widget triggering the validation.
        Returns:
            bool: True if the input 'P' is valid, False otherwise.
        """
        # Find the actual widget using its Tkinter name 'W'
        widget = self.nametowidget(W)
        # Get the custom name ('hour' or 'minute') we assigned earlier
        widget_type = getattr(widget, 'widget_name', None)

        # Allow the user to delete the content (empty string is okay temporarily)
        if not P:
            return True

        # Try converting the potential value 'P' to an integer
        try:
            value = int(P)
        except ValueError:
            # If it's not a number (e.g., user typed 'a'), it's invalid
            return False

        # Check if the number is within the allowed range based on widget type
        if widget_type == "hour":
            if 0 <= value <= 23:
                # Also check if the length is valid (max 2 digits for hours like '05', '12')
                return len(P) <= 2
            else:
                # Hour is outside 0-23 range
                return False
        elif widget_type == "minute":
            if 0 <= value <= 59:
                # Check length (max 2 digits for minutes like '00', '30', '59')
                return len(P) <= 2
            else:
                # Minute is outside 0-59 range
                return False
        else:
            # Should not happen if widget_name is set correctly
            return False


    def toggle_date_time_widgets(self):
        """
        Enables or disables the date calendar and the 'Set time' checkbutton
        based on whether the 'Set date' checkbutton is checked.
        """
        # Set state to 'normal' if checked, 'disabled' otherwise
        date_state = 'normal' if self.is_date_checked.get() else 'disabled'
        try:
            # Update the state of the calendar and the time checkbox
            self.cal.config(state=date_state)
            self.time_set_check.config(state=date_state)
        except tk.TclError:
             pass # Ignore error if widgets don't exist yet

        # If the date section is being disabled...
        if date_state == 'disabled':
            # ...also uncheck the 'Set time' checkbox...
            self.is_time_checked.set(0)
            try:
                # ...and disable the time spinboxes and reset their values.
                self.hour_spinbox.config(state='disabled')
                self.minute_spinbox.config(state='disabled')
                self.hour_var.set("00")
                self.minute_var.set("00")
            except tk.TclError:
                 pass
        else:
            # If date section is enabled, update the time widgets based on the 'Set time' checkbutton
            self.toggle_time_widgets()


    def toggle_time_widgets(self):
        """
        Enables or disables the hour and minute spinboxes based on
        whether the 'Set time' checkbutton is checked.
        """
        # Set state to 'normal' if checked (allows typing), 'disabled' otherwise
        time_state = 'normal' if self.is_time_checked.get() else 'disabled'
        try:
            # Update the state of both spinboxes
            self.hour_spinbox.config(state=time_state)
            self.minute_spinbox.config(state=time_state)
            # If disabling time, reset the values to "00"
            if time_state == 'disabled':
                self.hour_var.set("00")
                self.minute_var.set("00")
            # If enabling and the boxes are empty (e.g., first time), set to "00"
            elif time_state == 'normal' and not self.hour_var.get():
                 self.hour_var.set("00")
                 self.minute_var.set("00")
        except tk.TclError:
             pass # Ignore error if widgets don't exist yet


    def validate_inputs(self):
        """
        Performs final validation checks before saving the task.
        Checks description (required, unique), email format (basic),
        and ensures time isn't set without a date.
        Returns:
            bool: True if all checks pass, False otherwise (shows messagebox).
        """
        description = self.task_desc.get().strip()
        email_str = self.task_email.get().strip()

        # 1. Check if description is empty
        if not description:
            messagebox.showerror("Input Error", "Task description cannot be empty.")
            return False

        # 2. Check time consistency (though UI should prevent this)
        # Make sure 'Set time' isn't checked if 'Set date' isn't
        if not self.is_date_checked.get() and self.is_time_checked.get():
             messagebox.showerror("Input Error", "Cannot set time without setting a date.")
             return False
        # Also check if spinbox values are somehow invalid if time is checked
        if self.is_date_checked.get() and self.is_time_checked.get():
             try:
                 hour = int(self.hour_var.get())
                 minute = int(self.minute_var.get())
                 if not (0 <= hour <= 23 and 0 <= minute <= 59):
                      messagebox.showerror("Input Error", "Invalid hour or minute value detected.")
                      return False
             except ValueError:
                  messagebox.showerror("Input Error", "Hour and minute must be numeric.")
                  return False


        # 3. Check email format (simple check for '@' and '.')
        if email_str and not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email_str):
             messagebox.showerror("Input Error", "Invalid email format.")
             return False

        # 4. Check if description is unique (using controller method)
        is_editing = self.controller.add_or_edit.get() == "Edit Task"
        original_desc = self.controller.selected_task_desc.get() if is_editing else None
        # Pass current task ID if editing, so it doesn't compare against itself
        current_task_id = self.controller.selected_task_id.get() if is_editing else None

        # Only check uniqueness if the description has actually changed or it's a new task
        if description != original_desc:
             if not self.controller.is_desc_unique(description, current_task_id):
                 messagebox.showerror("Input Error", f"Task description '{description}' already exists.")
                 return False

        # All checks passed!
        return True


    def save_task(self):
        """
        Handles the process of saving the task (either creating new or updating existing).
        Called when the 'Save Task' button is clicked.
        """
        # First, run all validation checks. Stop if any fail.
        if not self.validate_inputs():
            # Try to put focus back on the likely problem field
            if not self.task_desc.get().strip():
                 self.task_desc_input.focus()
            # Add similar focus logic for email/time if needed
            return

        # Get values from the input fields
        desc = self.task_desc.get().strip()
        note = self.task_note_input.get("1.0", tk.END).strip() # Get text from 1st char to end

        # --- Get and Format Date ---
        due_date_str_for_db = None
        if self.is_date_checked.get():
            try:
                # Get date object from calendar
                selected_date_obj = self.cal.selection_get()
                # Format it as YYYY-MM-DD string for database consistency
                due_date_str_for_db = selected_date_obj.strftime('%Y-%m-%d')
            except Exception as e:
                 print(f"Error getting or formatting date from calendar: {e}")
                 messagebox.showerror("Error", "Could not retrieve valid date from calendar.")
                 return

        # --- Get and Format Time ---
        due_time = None
        if self.is_date_checked.get() and self.is_time_checked.get():
             try:
                 # Get values from spinboxes and format as HH:MM
                 hour = int(self.hour_var.get())
                 minute = int(self.minute_var.get())
                 due_time = f"{hour:02d}:{minute:02d}"
             except ValueError:
                 # Should be caught by validation, but double-check
                 messagebox.showerror("Save Error", "Invalid hour or minute value entered.")
                 return

        # Get email (or None if empty)
        email = self.task_email.get().strip() if self.task_email.get().strip() else None

        # Check if we are editing an existing task or adding a new one
        is_editing = self.controller.add_or_edit.get() == "Edit Task"
        success = False # Flag to track if DB operation worked

        if is_editing:
            # Get the ID of the task being edited
            task_id = self.controller.selected_task_id.get()
            # Call the database manager's update method
            success = self.controller.db_manager.update_task(
                task_id, desc, note, due_date_str_for_db, due_time, email
            )
        else: # Adding a new task
            # Create a new Task object with the details
            new_task = Task(desc, note, due_date_str_for_db, due_time, email)
            # Call the database manager's insert method
            success = self.controller.db_manager.insert_task(new_task)

        # If the database operation was successful...
        if success:
            # ...refresh the task list in the main frame...
            task_list = self.controller.db_manager.get_all_tasks()
            self.controller.fill_listbox(task_list)
            # ...switch back to the main tasks frame...
            self.show_tasks_frame()
            # ...and clear the input fields in this frame.
            self.clear_frame()
        # else: An error message was likely shown by validate_inputs or db_manager


    def clear_frame(self):
        """
        Resets all input fields and controls in the Add/Edit frame
        to their default states. Called after saving or cancelling.
        """
        self.task_desc.set("") # Clear description entry
        self.task_note_input.delete(1.0, "end") # Clear text area
        self.task_email.set("") # Clear email entry
        self.is_date_checked.set(0) # Uncheck 'Set date'
        self.is_time_checked.set(0) # Uncheck 'Set time'
        self.hour_var.set("00") # Reset hour spinbox
        self.minute_var.set("00") # Reset minute spinbox
        try:
             self.cal.selection_set(date.today()) # Reset calendar to today
        except: pass # Ignore error if today < mindate
        # Update the enabled/disabled state of widgets based on cleared checkboxes
        self.toggle_date_time_widgets()