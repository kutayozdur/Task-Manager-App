# app.py
# This is the main application file. It sets up the Tkinter window,
# manages the different frames (screens), handles database interactions (via DatabaseManager),
# and runs the email reminder thread.

import tkinter as tk
from tkinter import ttk, messagebox
from frames import Tasks, AddEdit, Info # Import the frame classes we created
from database_manager import DatabaseManager # Import the DB handling class
from datetime import date, datetime, timedelta # Need these for date/time logic
from task import Task # Import the Task class definition
import threading # For running email reminders in the background
import time      # For pausing the reminder thread
import smtplib   # For sending emails (Simple Mail Transfer Protocol)
from email.message import EmailMessage # For constructing email messages easily
import os        # To get environment variables for email credentials
import sys       # To help find resource paths when packaged (PyInstaller)
from dotenv import load_dotenv # To load environment variables from a .env file

# Load environment variables from .env file if it exists.
# This is useful for storing credentials locally during development.
load_dotenv()

# --- Configuration ---
# Define color constants for styling
COLOUR_PRIMARY = "#394867"
COLOUR_SECONDARY = "#212A3E"
COLOUR_LIGHT_BACKGROUND = "#F1F6F9"
COLOUR_LIGHT_TEXT = "#EEEEEE"
COLOUR_DARK_TEXT = "#212A3E"

# Email Configuration (Using environment variables for security)
# Make sure EMAIL_ADDRESS and EMAIL_PASSWORD are set in your environment or .env file
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com") # Default to Gmail SMTP server
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))           # Default to standard TLS port
EMAIL_SENDER_ADDRESS = os.getenv("EMAIL_ADDRESS")        # Your email address (sender)
EMAIL_SENDER_PASSWORD = os.getenv("EMAIL_PASSWORD")      # Your email app password
REMINDER_CHECK_INTERVAL_SECONDS = 60 # How often (in seconds) to check for reminders
REMINDER_WINDOW_MINUTES = 5          # How many minutes before due time to send reminder

# --- Helper Function ---
def get_resource_path(relative_path):
    """
    Gets the absolute path to a resource file (like the database).
    This helps find the file correctly whether running normally or as a packaged app (PyInstaller).
    """
    try:
        # If running as a PyInstaller bundle, the path is in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Otherwise, use the directory of the script file
        base_path = os.path.abspath(".")
    # Join the base path with the relative path of the resource
    return os.path.join(base_path, relative_path)

# --- Main Application Class ---
class TaskManager(tk.Tk):
    """
    The main application class. Inherits from tk.Tk to create the main window.
    Manages frames, database connection, and shared application state.
    """
    def __init__(self, *args, **kwargs):
        """
        Initializes the main application window and its components.
        """
        super().__init__(*args, **kwargs)

        # --- Style Configuration ---
        # Set up ttk styles for the application widgets
        style = ttk.Style(self)
        style.theme_use("clam") # Use a modern theme

        # Define custom styles for different frames and widgets
        style.configure("Tasks.TFrame", background=COLOUR_LIGHT_BACKGROUND)
        style.configure("Info.TFrame", background=COLOUR_LIGHT_BACKGROUND)
        style.configure("AddEdit.TFrame", background=COLOUR_LIGHT_BACKGROUND)
        style.configure("Background.TFrame", background=COLOUR_PRIMARY) # Main background
        style.configure("title.TLabel", background=COLOUR_PRIMARY, foreground=COLOUR_LIGHT_TEXT, font="Courier 38")
        style.configure("LightText_first.TLabel", background=COLOUR_PRIMARY, foreground=COLOUR_LIGHT_TEXT, font="Helvetica 16") # Field labels
        style.configure("LightText_second.TLabel", background=COLOUR_PRIMARY, foreground=COLOUR_LIGHT_TEXT, font="Helvetica 14") # Field values
        style.configure("button.TButton", background=COLOUR_SECONDARY, foreground=COLOUR_LIGHT_TEXT, font=("Helvetica", 12), padding=5)
        style.map("button.TButton", background=[("active", COLOUR_PRIMARY), ("disabled", "#555555")]) # Change color on hover/disable
        style.configure("checkbutton.TCheckbutton", background=COLOUR_PRIMARY, foreground=COLOUR_LIGHT_TEXT, font="Helvetica 12")
        style.map("checkbutton.TCheckbutton", background=[("active", COLOUR_PRIMARY)])
        style.configure("entry.TEntry", fieldbackground=COLOUR_SECONDARY, foreground=COLOUR_LIGHT_TEXT) # Style for Entry widgets
        style.configure("container.TFrame", background=COLOUR_PRIMARY) # Style for container frames

        # Set main window background and title
        self["background"] = COLOUR_PRIMARY
        self.title("Task Manager")
        self.resizable(False, False) # Prevent resizing the window

        # --- Database ---
        # Get the path to the database file using the helper function
        db_file = get_resource_path("task_database.db")
        # Create an instance of the DatabaseManager to handle DB operations
        self.db_manager = DatabaseManager(db_file)

        # --- Tkinter Variables ---
        # These variables are shared across different frames or hold application state.

        # Variable for the title of the Add/Edit frame ("Add Task" or "Edit Task")
        self.add_or_edit = tk.StringVar(value="Add Task")

        # Variables to hold the details of the currently selected task (used by Info and Add/Edit frames)
        self.selected_task_id = tk.IntVar()             # ID of the selected task
        self.selected_task_desc = tk.StringVar()        # Description
        self.selected_task_note = tk.StringVar()        # Note
        self.selected_task_date_str = tk.StringVar(value="N/A") # Due Date (string for display)
        self.selected_task_time_str = tk.StringVar(value="N/A") # Due Time (string for display)
        self.selected_task_email_str = tk.StringVar(value="N/A")# Email (string for display)
        self.selected_task_status_str = tk.StringVar(value="Pending") # Status ("Pending" or "Done")

        # --- Main Container Frame ---
        # This frame holds all other frames (Tasks, AddEdit, Info)
        container = ttk.Frame(self, style="container.TFrame")
        container.grid(row=0, column=0, sticky="nesw", padx=5, pady=5) # Fill the main window

        # --- Frames Initialization ---
        # Dictionary to store references to the different frame instances
        self.frames = dict()

        # Create instances of each frame (screen)
        # Pass 'self' (the controller) and necessary callback functions (lambdas) for switching frames.
        tasks_frame = Tasks(container, self, lambda: self.show_frame(AddEdit), lambda: self.show_frame(Info))
        add_edit_frame = AddEdit(container, self, lambda: self.show_frame(Tasks))
        info_frame = Info(container, self, lambda: self.show_frame(Tasks), lambda: self.show_frame(AddEdit))

        # Place all frames in the same grid cell; only one will be visible at a time.
        tasks_frame.grid(row=0, column=0, sticky="nesw")
        add_edit_frame.grid(row=0, column=0, sticky="nsew")
        info_frame.grid(row=0, column=0, sticky="nesw")

        # Store frame instances in the dictionary for easy access by class name
        self.frames[Tasks] = tasks_frame
        self.frames[AddEdit] = add_edit_frame
        self.frames[Info] = info_frame

        # --- Initial State ---
        # Load tasks from the database and populate the listbox in the Tasks frame
        self.fill_listbox(self.db_manager.get_all_tasks())
        # Show the main Tasks frame first when the app starts
        self.show_frame(Tasks)

        # --- Reminder Thread ---
        # Set up an event flag to signal the reminder thread to stop when the app closes.
        self.stop_reminder_event = threading.Event()
        # Create the background thread that will run the 'run_reminders' function.
        # daemon=True makes the thread exit automatically when the main app exits.
        self.reminder_thread = threading.Thread(target=self.run_reminders, daemon=True)
        # Start the reminder thread.
        self.reminder_thread.start()

        # --- Graceful Shutdown ---
        # Register a function ('on_closing') to be called when the user clicks the window's close button (X).
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def show_frame(self, container_class):
        """
        Brings the specified frame (identified by its class name) to the front, making it visible.
        Args:
            container_class: The class name of the frame to show (e.g., Tasks, AddEdit, Info).
        """
        frame = self.frames[container_class]
        # Special handling when switching to the AddEdit frame
        if container_class == AddEdit and self.add_or_edit.get() == "Add Task":
             # If we are adding a new task, clear any old input first
             frame.clear_frame()
             # Set focus to the description field automatically
             frame.task_desc_input.focus()
        elif container_class == Info:
             # When showing the Info frame, update the button states (Edit/Done)
             # based on the loaded task's status.
             frame.update_button_states()
        # Raise the requested frame to the top of the stacking order.
        frame.tkraise()

    def fill_listbox(self, task_list):
        """
        Populates the listbox in the Tasks frame with task descriptions.
        Sorts tasks by due date/time (if available) before displaying.
        Args:
            task_list (list[Task]): The list of Task objects to display.
        """
        listbox = self.frames[Tasks].tasks_listbox
        listbox.delete(0, tk.END) # Clear any existing items first

        # Define a sorting key function for tasks:
        # - Tasks with due date/time come first, sorted chronologically.
        # - Tasks without due date/time come after, sorted by ID (for stable order).
        def sort_key(task):
            dt = task.due_datetime # Get the combined datetime object (or None)
            # Return a tuple for sorting: (primary_key, secondary_key)
            return (0, dt) if dt else (1, task.id) # (0 means has date, 1 means no date)

        # Sort the task list using the defined key
        sorted_tasks = sorted(task_list, key=sort_key)

        # Dictionary to map the listbox index to the actual task ID.
        # This is needed because listbox indices can change if items are deleted/reordered.
        self.task_id_map = {}

        # Add each task to the listbox
        for index, task in enumerate(sorted_tasks):
            # Create the display text (description + optional date/time)
            display_text = f"{task.desc}"
            if task.due_date:
                display_text += f" ({task.due_date}"
                if task.due_time:
                    display_text += f" {task.due_time}"
                display_text += ")"
            # Add a marker if the task is done
            if task.status == 1:
                 display_text += " [Done]"
            # Insert the text into the listbox
            listbox.insert(tk.END, display_text)
            # Store the mapping: listbox index -> task ID
            self.task_id_map[index] = task.id

        # Optional: Color 'Done' items differently for visual cue
        for i in range(listbox.size()):
             item_text = listbox.get(i)
             if "[Done]" in item_text:
                 listbox.itemconfig(i, {'fg': 'grey'}) # Set color to grey
             else:
                 listbox.itemconfig(i, {'fg': COLOUR_LIGHT_TEXT}) # Use standard text color


    def on_double_click(self, event=None):
        """
        Handles the double-click event on an item in the Tasks listbox.
        Loads the selected task's details into the shared variables and shows the Info frame.
        Args:
            event: The event object passed by Tkinter (we don't use it directly here).
        """
        listbox = self.frames[Tasks].tasks_listbox
        selected_indices = listbox.curselection() # Get tuple of selected indices (usually just one)
        if not selected_indices:
            return # Do nothing if nothing is selected

        selected_index = selected_indices[0] # Get the index of the selected item
        try:
             # Look up the actual task ID using the map we created in fill_listbox
             task_id = self.task_id_map[selected_index]
        except KeyError:
             # This might happen if the map is out of sync (shouldn't normally occur)
             messagebox.showerror("Error", "Could not find the selected task ID.")
             return

        # Retrieve the full task details from the database using the ID
        selected_task = self.db_manager.get_task_by_id(task_id)

        if not selected_task:
             # If task not found in DB (maybe deleted unexpectedly?)
             messagebox.showerror("Error", f"Task with ID {task_id} not found in database.")
             # Refresh the listbox to reflect the current DB state
             self.fill_listbox(self.db_manager.get_all_tasks())
             return

        # --- Update the shared Tkinter variables ---
        # These variables are linked to the labels in the Info frame, so updating them
        # automatically updates the Info screen when it's shown.
        self.selected_task_id.set(selected_task.id)
        self.selected_task_desc.set(selected_task.desc)
        # Use empty string if note is None, otherwise use the note
        self.selected_task_note.set(selected_task.note if selected_task.note else "")
        # Display date/time/email or "N/A" if they don't exist
        self.selected_task_date_str.set(selected_task.due_date if selected_task.due_date else "N/A")
        self.selected_task_time_str.set(selected_task.due_time if selected_task.due_time else "N/A")
        self.selected_task_email_str.set(selected_task.email if selected_task.email else "N/A")
        # Set status string based on the status value (0 or 1)
        self.selected_task_status_str.set("Pending" if selected_task.status == 0 else "Done")

        # Switch to the Info frame to display these details
        self.show_frame(Info)


    def change_status(self, task_id):
        """
        Marks a task as 'Done' in the database and updates the UI.
        Args:
            task_id (int): The ID of the task to mark as done.
        """
        self.db_manager.update_status(task_id) # Update the database
        self.selected_task_status_str.set("Done") # Update the shared variable (for Info frame)
        # Refresh the main listbox to show the "[Done]" marker and potentially re-sort/re-color
        self.fill_listbox(self.db_manager.get_all_tasks())
        # Update the button states in the Info frame (disable Edit/Done buttons)
        # Need to access the frame instance directly here
        self.frames[Info].update_button_states()


    def delete_task(self, task_id):
        """
        Deletes a task from the database. (Actual deletion logic is in db_manager).
        Args:
            task_id (int): The ID of the task to delete.
        """
        self.db_manager.delete_task(task_id)


    def show_delete_confirmation(self, task_id):
        """
        Shows a confirmation dialog box before deleting a task.
        Args:
            task_id (int): The ID of the task potentially being deleted.
        """
        # Get the task description to show in the confirmation message
        task = self.db_manager.get_task_by_id(task_id)
        task_name = task.desc if task else f"Task ID {task_id}" # Use description or ID if task not found

        # Ask the user for confirmation
        yes_no = messagebox.askyesno(
            title="Confirm Deletion",
            message=f"Are you sure you want to delete the task '{task_name}'?\nThis action cannot be undone.",
            icon='warning' # Show a warning icon
        )
        # If the user clicks "Yes"...
        if yes_no:
            self.delete_task(task_id) # ...delete the task...
            # ...refresh the main listbox...
            task_list = self.db_manager.get_all_tasks()
            self.fill_listbox(task_list)
            # ...and switch back to the Tasks frame.
            self.show_frame(Tasks)
        # else: User clicked "No", do nothing.


    def edit_task_prep(self):
        """
        Prepares the AddEdit frame for editing the currently selected task.
        Populates the input fields with the selected task's details.
        Called before switching to the AddEdit frame for editing.
        """
        frame = self.frames[AddEdit] # Get the AddEdit frame instance
        self.add_or_edit.set("Edit Task") # Set the title label for the frame

        # Populate the input fields using the shared selected_task variables
        frame.task_desc.set(self.selected_task_desc.get())
        # For the Text widget, need to delete existing content then insert new
        frame.task_note_input.delete("1.0", tk.END)
        frame.task_note_input.insert("1.0", self.selected_task_note.get())
        # Set email, use empty string if it was "N/A"
        frame.task_email.set(self.selected_task_email_str.get() if self.selected_task_email_str.get() != "N/A" else "")

        # --- Handle Date and Time Setup ---
        # Check if the selected task has a date
        has_date = self.selected_task_date_str.get() != "N/A"
        # Set the 'Set date' checkbox accordingly
        frame.is_date_checked.set(1 if has_date else 0)

        if has_date:
             # If date exists, enable the calendar and select the task's date
             frame.cal.config(state='normal')
             try:
                 frame.cal.selection_set(self.selected_task_date_str.get())
             except Exception as e:
                 print(f"Error setting calendar date during edit prep: {e}")
                 frame.cal.selection_set(date.today()) # Fallback to today

             # Check if the task also has a time
             has_time = self.selected_task_time_str.get() != "N/A"
             # Set the 'Set time' checkbox accordingly
             frame.is_time_checked.set(1 if has_time else 0)
             # Enable the 'Set time' checkbox itself
             frame.time_set_check.config(state='normal')

             if has_time:
                 # If time exists, parse the HH:MM string and set the spinbox values
                 try:
                     time_parts = self.selected_task_time_str.get().split(':')
                     hour = int(time_parts[0])
                     minute = int(time_parts[1])
                     # Set spinbox variables (ensuring format like '05')
                     frame.hour_var.set(f"{hour:02d}")
                     frame.minute_var.set(f"{minute:02d}")
                     # Enable the spinboxes
                     frame.hour_spinbox.config(state='normal')
                     frame.minute_spinbox.config(state='normal')
                 except (IndexError, ValueError, TypeError) as e:
                     # If parsing fails (e.g., bad time format stored somehow)
                     print(f"Error parsing time '{self.selected_task_time_str.get()}' during edit prep: {e}")
                     # Reset time fields to default/disabled state
                     frame.hour_var.set("00")
                     frame.minute_var.set("00")
                     frame.hour_spinbox.config(state='disabled')
                     frame.minute_spinbox.config(state='disabled')
                     frame.is_time_checked.set(0) # Uncheck 'Set time' if it was invalid
             else:
                 # If task has date but no time, reset/disable time fields
                 frame.hour_var.set("00")
                 frame.minute_var.set("00")
                 frame.hour_spinbox.config(state='disabled')
                 frame.minute_spinbox.config(state='disabled')

        else: # Task has no date
            # Disable all date/time controls and reset values
            frame.is_time_checked.set(0)
            frame.hour_var.set("00")
            frame.minute_var.set("00")
            frame.cal.config(state='disabled')
            frame.time_set_check.config(state='disabled')
            frame.hour_spinbox.config(state='disabled')
            frame.minute_spinbox.config(state='disabled')
            try:
                 frame.cal.selection_set(date.today()) # Reset calendar selection
            except: pass

        # Set focus to the description field when starting to edit
        frame.task_desc_input.focus()


    def is_desc_unique(self, new_desc, current_task_id=None):
         """
         Checks if a given task description is unique among all tasks.
         Optionally excludes a specific task ID from the check (used during editing).
         Args:
             new_desc (str): The description string to check for uniqueness.
             current_task_id (int, optional): The ID of the task being edited, to exclude it
                                             from the uniqueness check against itself. Defaults to None.
         Returns:
             bool: True if the description is unique (or belongs to current_task_id), False otherwise.
         """
         tasks = self.db_manager.get_all_tasks() # Get all tasks
         for task in tasks:
             # If we are editing (current_task_id is provided) and this task is the one
             # we are currently editing, skip the comparison with itself.
             if current_task_id is not None and task.id == current_task_id:
                 continue
             # Compare the new description (case-insensitive) with existing ones
             if new_desc.strip().lower() == task.desc.strip().lower():
                 return False # Found a duplicate description
         return True # No duplicates found


    # --- Email Reminder Logic ---

    def run_reminders(self):
        """
        The main function for the background reminder thread.
        Periodically checks the database for tasks due soon and sends email reminders.
        Runs in a loop until the stop_reminder_event is set.
        """
        print("---- Reminder thread started ----")
        # Loop indefinitely until the main app signals to stop
        while not self.stop_reminder_event.is_set():
            try:
                # Get the current local time
                now = datetime.now()
                print(f"\n[{now.strftime('%Y-%m-%d %H:%M:%S')}] Reminder check running...")
                # Get tasks eligible for reminders from the database
                tasks_to_check = self.db_manager.get_tasks_for_reminder()

                if not tasks_to_check:
                    print("  - No tasks found needing reminders (pending, with date, time, and email).")
                else:
                     print(f"  - Found {len(tasks_to_check)} potential task(s) for reminder.")

                # Iterate through the eligible tasks
                for task in tasks_to_check:
                    print(f"  - Checking task: ID={task.id}, Desc='{task.desc}', DueDate={task.due_date}, DueTime={task.due_time}, Email={task.email}, Status={task.status}")
                    # Get the combined datetime object for the task's due date/time
                    due_dt = task.due_datetime
                    if due_dt: # Proceed only if date/time was parsed correctly
                        # Calculate the start time for the reminder window
                        reminder_time_start = due_dt - timedelta(minutes=REMINDER_WINDOW_MINUTES)
                        # Check if the current time 'now' is within the reminder window
                        is_condition_met = reminder_time_start <= now < due_dt
                        print(f"    - Task {task.id}: Now='{now}', Due='{due_dt}', ReminderStart='{reminder_time_start}'")
                        print(f"    - Condition Met (ReminderStart <= Now < Due): {is_condition_met}")

                        # If the current time is within the window...
                        if is_condition_met:
                             print(f"    ======> Sending reminder for task: '{task.desc}' (ID: {task.id}) to {task.email}")
                             # ...call the function to send the actual email...
                             self.send_reminder_email(task)
                             # IMPORTANT TODO: Implement logic to mark this task as 'reminder sent'
                             # in the database to prevent sending multiple emails for the same task.
                             # This would require adding a 'reminder_sent' column to the DB
                             # and updating it here.
                    else:
                         # Log if date/time parsing failed for a task
                         print(f"    - Task {task.id}: Could not parse due_datetime (Date: {task.due_date}, Time: {task.due_time}).")

            except Exception as e:
                # Catch any unexpected errors during the reminder check loop
                print(f"!!!!!!!! ERROR in reminder thread loop: {e} !!!!!!!!")
                import traceback
                traceback.print_exc() # Print the full error details

            # Pause the thread for the specified interval before the next check
            # print(f" Reminder check finished. Waiting {REMINDER_CHECK_INTERVAL_SECONDS} seconds...")
            # Wait efficiently using the event flag (allows quick exit if stop is signaled)
            self.stop_reminder_event.wait(REMINDER_CHECK_INTERVAL_SECONDS)

        print("---- Reminder thread stopped ----")


    def send_reminder_email(self, task):
        """
        Constructs and sends the reminder email for a specific task.
        Uses smtplib to connect to the SMTP server and send the message.
        Args:
            task (Task): The task object for which to send a reminder.
        """
        # Check if necessary email configuration exists
        if not task.email or not EMAIL_SENDER_ADDRESS or not EMAIL_SENDER_PASSWORD:
            print("Email configuration incomplete (sender/password/recipient missing), cannot send reminder.")
            return
        if not SMTP_SERVER:
             print("SMTP server not configured, cannot send reminder.")
             return

        # Create the email message object
        msg = EmailMessage()
        msg['Subject'] = f"Task Reminder: {task.desc}" # Email subject
        msg['From'] = EMAIL_SENDER_ADDRESS           # Sender address
        msg['To'] = task.email                       # Recipient address (from task)

        # Format the due date and time nicely for the email body
        due_datetime_obj = task.due_datetime
        due_time_str = due_datetime_obj.strftime('%I:%M %p') if due_datetime_obj else "N/A" # e.g., 02:30 PM
        due_date_str = due_datetime_obj.strftime('%A, %B %d, %Y') if due_datetime_obj else "N/A" # e.g., Tuesday, May 06, 2025

        # Construct the email body
        body = f"Hi,\n\nThis is a reminder for your upcoming task:\n\n"
        body += f"  Task:       {task.desc}\n"
        if task.note: # Only include note if it exists
             body += f"  Note:       {task.note}\n"
        body += f"  Due:        {due_date_str} at {due_time_str}\n\n"
        body += f"Task Manager App\n" # Signature

        # Set the email content
        msg.set_content(body)

        # --- Try sending the email ---
        try:
            print(f"    - Attempting to connect to SMTP server: {SMTP_SERVER}:{SMTP_PORT}")
            # Connect to the SMTP server (using 'with' ensures connection is closed)
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as server: # Added timeout
                # print("    - Connection successful. Starting TLS...") # Debug
                server.starttls() # Secure the connection using TLS
                # print("    - TLS started. Logging in...") # Debug
                # Log in to the sender's email account
                server.login(EMAIL_SENDER_ADDRESS, EMAIL_SENDER_PASSWORD)
                # print("    - Login successful. Sending message...") # Debug
                # Send the email message
                server.send_message(msg)
                # print("    - Message sent.") # Debug
            print(f"    - Reminder email sent successfully to {task.email} for task '{task.desc}'.")
        except smtplib.SMTPAuthenticationError:
             # Handle login failure (wrong email/password/app password)
             print(f"    - SMTP Authentication Error: Failed to login for email '{EMAIL_SENDER_ADDRESS}'. Check email/password/app password.")
        except smtplib.SMTPConnectError:
             # Handle failure to connect to the server
             print(f"    - SMTP Connect Error: Failed to connect to server '{SMTP_SERVER}:{SMTP_PORT}'. Check server/port.")
        except smtplib.SMTPServerDisconnected:
             print(f"    - SMTP Error: Server disconnected unexpectedly.")
        except TimeoutError:
             print(f"    - SMTP Error: Connection to server timed out.")
        except Exception as e:
            # Catch any other exceptions during email sending
            print(f"    - Failed to send email reminder for task '{task.desc}' to {task.email}: {e}")
            import traceback
            traceback.print_exc() # Print full traceback for unexpected errors


    def on_closing(self):
        """
        Handles the application closing sequence.
        Called when the user closes the window (e.g., clicks the 'X' button or the Exit button).
        """
        print("Closing application...")
        # Signal the reminder thread that it should stop its loop
        self.stop_reminder_event.set()
        # Wait a very short time to allow the thread to potentially finish its current cycle cleanly
        # self.reminder_thread.join(timeout=0.5) # Optional: uncomment to wait slightly longer

        # Close the database connection gracefully
        if self.db_manager:
            self.db_manager.close()
        # Destroy the main Tkinter window
        self.destroy()
        print("Application closed.")


# --- Main Execution Block ---
# This code runs only when the script is executed directly (not imported as a module).
if __name__ == "__main__":
    try:
        # Create an instance of the main application class
        app = TaskManager()
        # Start the Tkinter event loop (makes the window appear and responsive)
        app.mainloop()
    except Exception as e:
        # Catch any unexpected errors during application startup or runtime
        print("An error occurred:")
        import traceback
        traceback.print_exc() # Print the full error details to the console
        input("Press Enter to exit...") # Pause so the user can see the error before closing