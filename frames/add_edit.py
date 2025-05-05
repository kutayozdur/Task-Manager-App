import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import Calendar
from datetime import date, datetime
import re
from task import Task
from tkinter import font

class AddEdit(ttk.Frame):
    def __init__(self, parent, controller, show_tasks_frame):
        super().__init__(parent)

        self["style"] = "Background.TFrame"

        entry_font = font.Font(family="Rockwell", size=16)
        label_font = font.Font(family="Helvetica", size=14)
        spinbox_font = font.Font(family="Rockwell", size=18)

        self.controller = controller
        self.show_tasks_frame = show_tasks_frame

        # --- Validation Setup ---
        # Register validation functions (returns a Tcl command string)
        self.validate_hour_cmd = self.register(self.validate_spinbox_input)
        self.validate_minute_cmd = self.register(self.validate_spinbox_input)


        # --- Variables ---
        self.task_desc = tk.StringVar()
        self.task_email = tk.StringVar()
        self.is_date_checked = tk.IntVar()
        self.is_time_checked = tk.IntVar()
        self.hour_var = tk.StringVar(value="00")
        self.minute_var = tk.StringVar(value="00")


        # --- Widgets ---
        ttk.Label(self, textvariable=controller.add_or_edit, style="title.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", padx=20, pady=10
        )

        main_container = ttk.Frame(self, style="container.TFrame")
        main_container.grid(row=1, column=0, sticky="nsew", padx=40, pady=10)
        main_container.columnconfigure(1, weight=1)

        # Description, Note... (keep as before)
        # ...
        ttk.Label(
            main_container, text="*Description:", style="LightText_first.TLabel", font=label_font
        ).grid(row=0, column=0, sticky="w", padx=10, pady=10)
        self.task_desc_input = ttk.Entry(
            main_container, textvariable=self.task_desc, width=40, font=entry_font
        )
        self.task_desc_input.grid(row=0, column=1, sticky="ew", padx=10, pady=5)

        ttk.Label(
            main_container, text="Note:", style="LightText_first.TLabel", font=label_font
        ).grid(row=1, column=0, sticky="nw", padx=10, pady=10)
        self.task_note_input = tk.Text(
            main_container, width=40, height=4, font=entry_font,
            background="#212A3E", foreground="#EEEEEE", insertbackground="#EEEEEE"
        )
        self.task_note_input.grid(row=1, column=1, sticky="ew", padx=10, pady=5)

        # --- Date & Time Section ---
        datetime_frame = ttk.Frame(main_container, style="container.TFrame")
        datetime_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        datetime_frame.columnconfigure(1, weight=1)

        # Date Checkbutton & Calendar... (keep as before)
        # ...
        self.date_set_check = ttk.Checkbutton(
            datetime_frame, padding=5, text="Set date", variable=self.is_date_checked,
            command=self.toggle_date_time_widgets, style="checkbutton.TCheckbutton"
        )
        self.date_set_check.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        self.cal = Calendar(
            datetime_frame, selectmode="day", mindate=date.today(), showweeknumbers=False,
            disableddaybackground="grey", disableddayforeground="darkgrey",
            state='disabled'
        )
        self.cal.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        try:
            self.cal.selection_set(date.today())
        except: pass


        # Time Checkbutton & Spinboxes
        self.time_set_check = ttk.Checkbutton(
            datetime_frame, padding=5, text="Set time", variable=self.is_time_checked,
            command=self.toggle_time_widgets, style="checkbutton.TCheckbutton", state='disabled'
        )
        self.time_set_check.grid(row=0, column=2, sticky="w", padx=(20, 5), pady=5)

        time_spinbox_frame = ttk.Frame(datetime_frame, style="container.TFrame")
        time_spinbox_frame.grid(row=1, column=2, sticky="w", padx=(20, 10), pady=5)

        # Hour Spinbox - Added validation
        self.hour_spinbox = ttk.Spinbox(
            time_spinbox_frame, from_=0, to=23, wrap=True, width=3, state='disabled',
            textvariable=self.hour_var, format="%02.0f",
            font=spinbox_font,
            # --- ADDED VALIDATION ---
            validate='key', # Validate whenever a key is pressed
             # Pass the new value (%P) and widget name (%W) to the validation function
            validatecommand=(self.validate_hour_cmd, '%P', '%W')
        )
        self.hour_spinbox.grid(row=0, column=0, padx=(0,2), pady=2)
        # Set a name for the widget to identify it in the validation function
        self.hour_spinbox.widget_name = "hour"


        ttk.Label(time_spinbox_frame, text=":", style="LightText_first.TLabel", font=spinbox_font).grid(row=0, column=1, padx=0, pady=2)

        # Minute Spinbox - Added validation
        self.minute_spinbox = ttk.Spinbox(
            time_spinbox_frame, from_=0, to=59, wrap=True, width=3, state='disabled',
            textvariable=self.minute_var, format="%02.0f",
            font=spinbox_font,
            # --- ADDED VALIDATION ---
            validate='key',
            validatecommand=(self.validate_minute_cmd, '%P', '%W')
        )
        self.minute_spinbox.grid(row=0, column=2, padx=(2,0), pady=2)
        self.minute_spinbox.widget_name = "minute" # Set widget name


        # --- Email Section --- (keep as before)
        # ...
        ttk.Label(
            main_container, text="Email (for reminder):", style="LightText_first.TLabel", font=label_font
        ).grid(row=3, column=0, sticky="w", padx=10, pady=10)
        self.task_email_input = ttk.Entry(
            main_container, textvariable=self.task_email, width=40, font=entry_font
        )
        self.task_email_input.grid(row=3, column=1, sticky="ew", padx=10, pady=5)

        # --- Buttons --- (keep as before)
        # ...
        button_container = ttk.Frame(self, padding=10, style="container.TFrame")
        button_container.grid(row=4, column=0, sticky="ew", padx=10, pady=10)
        button_container.columnconfigure((0, 1), weight=1)

        self.cancel_button = ttk.Button(
            button_container, text="Cancel", style="button.TButton",
            command=lambda: [show_tasks_frame(), self.clear_frame()]
        )
        self.cancel_button.grid(row=0, column=0, sticky="e", padx=10)

        self.done_button = ttk.Button(
            button_container, text="Save Task", style="button.TButton",
            command=self.save_task
        )
        self.done_button.grid(row=0, column=1, sticky="e", padx=10)

        # Initial setup
        self.toggle_date_time_widgets()

    # --- Validation Function ---
    def validate_spinbox_input(self, P, W):
        """
        Validates the input for hour and minute spinboxes.
        P: The value the text will have if the change is allowed.
        W: The widget name (we manually set .widget_name on the spinboxes).
        """
        widget = self.nametowidget(W) # Get the actual widget instance
        widget_type = getattr(widget, 'widget_name', None)

        if not P: # Allow empty string (e.g., when deleting content)
            return True

        try:
            value = int(P)
        except ValueError:
            # Not an integer
            return False

        # Check range based on widget type
        if widget_type == "hour":
            if 0 <= value <= 23:
                 # Check length constraint - allow max 2 digits
                return len(P) <= 2
            else:
                return False
        elif widget_type == "minute":
            if 0 <= value <= 59:
                # Check length constraint - allow max 2 digits
                return len(P) <= 2
            else:
                return False
        else:
            # Unknown widget - should not happen
            return False


    def toggle_date_time_widgets(self):
        """Enable/disable date and time widgets based on the 'Set date' checkbutton."""
        date_state = 'normal' if self.is_date_checked.get() else 'disabled'
        try:
            self.cal.config(state=date_state)
            self.time_set_check.config(state=date_state)
        except tk.TclError:
             pass

        if date_state == 'disabled':
            self.is_time_checked.set(0)
            try:
                # --- Set state to 'disabled' ---
                self.hour_spinbox.config(state='disabled')
                self.minute_spinbox.config(state='disabled')
                self.hour_var.set("00")
                self.minute_var.set("00")
            except tk.TclError:
                 pass
        else:
            self.toggle_time_widgets()


    def toggle_time_widgets(self):
        """Enable/disable the time spinboxes based on the 'Set time' checkbutton."""
        # --- Set state to 'normal' to allow typing ---
        time_state = 'normal' if self.is_time_checked.get() else 'disabled'
        try:
            self.hour_spinbox.config(state=time_state)
            self.minute_spinbox.config(state=time_state)
            if time_state == 'disabled':
                self.hour_var.set("00")
                self.minute_var.set("00")
            elif time_state == 'normal' and not self.hour_var.get(): # Set default if enabling and empty
                 self.hour_var.set("00")
                 self.minute_var.set("00")
        except tk.TclError:
             pass

    # validate_inputs function remains the same (no longer needs time format check)
    # ...
    def validate_inputs(self):
        """Validate description, and email format."""
        description = self.task_desc.get().strip()
        email_str = self.task_email.get().strip()

        # 1. Description validation
        if not description:
            messagebox.showerror("Input Error", "Task description cannot be empty.")
            return False

        # 2. Time validation (Check if spinbox values make sense if time is checked)
        if self.is_date_checked.get() and self.is_time_checked.get():
             # Additional check: Ensure the values aren't somehow invalid despite validation
             # This might happen if validation fails subtly or state changes occur unexpectedly
             try:
                 hour = int(self.hour_var.get())
                 minute = int(self.minute_var.get())
                 if not (0 <= hour <= 23 and 0 <= minute <= 59):
                      messagebox.showerror("Input Error", "Invalid hour or minute value detected.")
                      return False
             except ValueError:
                  messagebox.showerror("Input Error", "Hour and minute must be numeric.")
                  return False

        elif not self.is_date_checked.get() and self.is_time_checked.get():
             messagebox.showerror("Input Error", "Cannot set time without setting a date.")
             return False

        # 3. Email validation
        if email_str and not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email_str):
             messagebox.showerror("Input Error", "Invalid email format.")
             return False

        # 4. Description uniqueness check
        is_editing = self.controller.add_or_edit.get() == "Edit Task"
        original_desc = self.controller.selected_task_desc.get() if is_editing else None
        current_task_id = self.controller.selected_task_id.get() if is_editing else None

        if description != original_desc:
             if not self.controller.is_desc_unique(description, current_task_id):
                 messagebox.showerror("Input Error", f"Task description '{description}' already exists.")
                 return False

        return True


    def save_task(self):
        """Handles both creating and editing tasks after validation."""
        if not self.validate_inputs():
            # ... (focus logic if needed) ...
            return

        desc = self.task_desc.get().strip()
        note = self.task_note_input.get("1.0", tk.END).strip()

        # --- MODIFIED DATE HANDLING ---
        # due_date = self.cal.get_date() if self.is_date_checked.get() else None # Old way
        due_date_str_for_db = None # Initialize variable for the string to save
        if self.is_date_checked.get():
            try:
                # Get the raw date object from the calendar selection
                selected_date_obj = self.cal.selection_get() # Returns datetime.date
                # Format the date object into the standard YYYY-MM-DD string
                due_date_str_for_db = selected_date_obj.strftime('%Y-%m-%d')
            except Exception as e:
                 # Handle cases where date might not be selected properly
                 print(f"Error getting or formatting date from calendar: {e}")
                 messagebox.showerror("Input Error", "Could not retrieve a valid date from the calendar.")
                 return # Stop saving if date is invalid
        # --- END OF MODIFIED DATE HANDLING ---


        due_time = None
        if self.is_date_checked.get() and self.is_time_checked.get():
             try:
                 hour = int(self.hour_var.get())
                 minute = int(self.minute_var.get())
                 due_time = f"{hour:02d}:{minute:02d}"
             except ValueError:
                 messagebox.showerror("Save Error", "Invalid hour or minute value entered.")
                 return

        email = self.task_email.get().strip() if self.task_email.get().strip() else None

        is_editing = self.controller.add_or_edit.get() == "Edit Task"
        success = False

        if is_editing:
            task_id = self.controller.selected_task_id.get()
            # Pass the correctly formatted date string (or None)
            success = self.controller.db_manager.update_task(task_id, desc, note, due_date_str_for_db, due_time, email)
        else:
            # Pass the correctly formatted date string (or None)
            new_task = Task(desc, note, due_date_str_for_db, due_time, email)
            success = self.controller.db_manager.insert_task(new_task)

        if success:
            task_list = self.controller.db_manager.get_all_tasks()
            self.controller.fill_listbox(task_list)
            self.show_tasks_frame()
            self.clear_frame()

    # clear_frame function remains the same
    # ...
    def clear_frame(self):
        """Clears all input fields and resets checkboxes/spinboxes."""
        self.task_desc.set("")
        self.task_note_input.delete(1.0, "end")
        self.task_email.set("")
        self.is_date_checked.set(0)
        self.is_time_checked.set(0)
        self.hour_var.set("00")
        self.minute_var.set("00")
        try:
             self.cal.selection_set(date.today())
        except: pass
        self.toggle_date_time_widgets()

# Need to update app.py edit_task_prep slightly if state changed
# from 'readonly' to 'normal'