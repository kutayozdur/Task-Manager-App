import tkinter as tk
from tkinter import ttk, messagebox
from frames import Tasks, AddEdit, Info
from database_manager import DatabaseManager
from datetime import date, datetime, timedelta # Added datetime, timedelta
from task import Task
import threading # Added for reminder thread
import time # Added for reminder thread sleep
import smtplib # Added for sending email
from email.message import EmailMessage # Added for constructing email
import os # Added to help find db path
import sys # Added to help find db path
from dotenv import load_dotenv

load_dotenv()


# --- Configuration ---
COLOUR_PRIMARY = "#394867"
COLOUR_SECONDARY = "#212A3E"
COLOUR_LIGHT_BACKGROUND = "#F1F6F9"
COLOUR_LIGHT_TEXT = "#EEEEEE"
COLOUR_DARK_TEXT = "#212A3E"

# Email Configuration (Replace with your actual details or use environment variables/config file)
SMTP_SERVER = "smtp.gmail.com" # e.g., "smtp.gmail.com" or your server
SMTP_PORT = 587 # Standard port for TLS
EMAIL_SENDER_ADDRESS = os.getenv("EMAIL_ADDRESS") # Your email
EMAIL_SENDER_PASSWORD = os.getenv("EMAIL_APP") # Use an App Password if using Gmail 2FA
REMINDER_CHECK_INTERVAL_SECONDS = 60 # Check every 60 seconds
REMINDER_WINDOW_MINUTES = 5 # Remind 5 minutes before due time

# --- Helper to find DB path ---
def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class TaskManager(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # --- Style Configuration ---
        style = ttk.Style(self)
        style.theme_use("clam")
        # (Keep existing style configurations...)
        style.configure("Tasks.TFrame", background=COLOUR_LIGHT_BACKGROUND)
        style.configure("Info.TFrame", background=COLOUR_LIGHT_BACKGROUND)
        style.configure("AddEdit.TFrame", background=COLOUR_LIGHT_BACKGROUND)
        style.configure("Background.TFrame", background=COLOUR_PRIMARY)
        style.configure("title.TLabel", background=COLOUR_PRIMARY, foreground=COLOUR_LIGHT_TEXT, font="Courier 38")
        style.configure("LightText_first.TLabel", background=COLOUR_PRIMARY, foreground=COLOUR_LIGHT_TEXT, font="Helvetica 16") # Adjusted size
        style.configure("LightText_second.TLabel", background=COLOUR_PRIMARY, foreground=COLOUR_LIGHT_TEXT, font="Helvetica 14") # Adjusted size
        style.configure("button.TButton", background=COLOUR_SECONDARY, foreground=COLOUR_LIGHT_TEXT, font=("Helvetica", 12), padding=5) # Added font/padding
        style.map("button.TButton", background=[("active", COLOUR_PRIMARY), ("disabled", "#555555")]) # Added disabled mapping
        style.configure("checkbutton.TCheckbutton", background=COLOUR_PRIMARY, foreground=COLOUR_LIGHT_TEXT, font="Helvetica 12") # Adjusted size
        style.map("checkbutton.TCheckbutton", background=[("active", COLOUR_PRIMARY)])
        style.configure("entry.TEntry", fieldbackground=COLOUR_SECONDARY, foreground=COLOUR_LIGHT_TEXT) # Use fieldbackground
        style.configure("container.TFrame", background=COLOUR_PRIMARY)


        self["background"] = COLOUR_PRIMARY
        self.title("Task Manager")
        self.resizable(False, False)

        # --- Database ---
        # Use get_resource_path to make it work with PyInstaller
        db_file = get_resource_path("task_database.db")
        # db_file = "task_database.db" # Simpler path for development if needed
        self.db_manager = DatabaseManager(db_file)


        # --- Tkinter Variables ---
        # For Add/Edit frame title
        self.add_or_edit = tk.StringVar(value="Add Task")
        # For Info/Edit frame data binding
        self.selected_task_id = tk.IntVar()
        self.selected_task_desc = tk.StringVar()
        self.selected_task_note = tk.StringVar()
        self.selected_task_date_str = tk.StringVar(value="N/A") # Display string for date
        self.selected_task_time_str = tk.StringVar(value="N/A") # Display string for time
        self.selected_task_email_str = tk.StringVar(value="N/A") # Display string for email
        self.selected_task_status_str = tk.StringVar(value="Pending") # Display string for status


        # --- Main Container ---
        container = ttk.Frame(self, style="container.TFrame") # Apply style
        container.grid(row=0, column=0, sticky="nesw", padx=5, pady=5) # Add padding


        # --- Frames Initialization ---
        self.frames = dict()

        tasks_frame = Tasks(container, self, lambda: self.show_frame(AddEdit), lambda: self.show_frame(Info))
        tasks_frame.grid(row=0, column=0, sticky="nesw")

        add_edit_frame = AddEdit(container, self, lambda: self.show_frame(Tasks))
        add_edit_frame.grid(row=0, column=0, sticky="nsew")

        info_frame = Info(container, self, lambda: self.show_frame(Tasks), lambda: self.show_frame(AddEdit))
        info_frame.grid(row=0, column=0, sticky="nsew")

        self.frames[Tasks] = tasks_frame
        self.frames[AddEdit] = add_edit_frame
        self.frames[Info] = info_frame

        # --- Initial State ---
        self.fill_listbox(self.db_manager.get_all_tasks())
        self.show_frame(Tasks)

        # --- Reminder Thread ---
        self.stop_reminder_event = threading.Event()
        self.reminder_thread = threading.Thread(target=self.run_reminders, daemon=True) # daemon=True ensures thread exits with app
        self.reminder_thread.start()

        # --- Graceful Shutdown ---
        self.protocol("WM_DELETE_WINDOW", self.on_closing)


    def show_frame(self, container_class):
        """Raises the specified frame to the top."""
        frame = self.frames[container_class]
        # If switching to AddEdit, ensure frame is cleared unless editing
        if container_class == AddEdit and self.add_or_edit.get() == "Add Task":
             frame.clear_frame()
             frame.task_desc_input.focus() # Set focus on description
        elif container_class == Info:
             # Update button states when showing Info frame
             frame.update_button_states()

        frame.tkraise()


    def fill_listbox(self, task_list):
        """Clears and refills the listbox, sorting by date/time."""
        listbox = self.frames[Tasks].tasks_listbox
        listbox.delete(0, tk.END)

        # Sort tasks: by due datetime (if available), then by ID (for consistency)
        def sort_key(task):
            dt = task.due_datetime
            # Return a tuple: tasks with dates/times first, sorted, then others by ID
            return (0, dt) if dt else (1, task.id)

        sorted_tasks = sorted(task_list, key=sort_key)

        # Fill the listbox with task descriptions and store ID mapping
        self.task_id_map = {} # Maps listbox index to task ID
        for index, task in enumerate(sorted_tasks):
            display_text = f"{task.desc}"
            if task.due_date:
                display_text += f" ({task.due_date}"
                if task.due_time:
                    display_text += f" {task.due_time}"
                display_text += ")"
            if task.status == 1:
                 display_text += " [Done]"
            listbox.insert(tk.END, display_text)
            self.task_id_map[index] = task.id # Store ID associated with this listbox entry

        # Optional: Color 'Done' items differently
        for i in range(listbox.size()):
             item_text = listbox.get(i)
             if "[Done]" in item_text:
                 listbox.itemconfig(i, {'fg': 'grey'})
             else:
                 listbox.itemconfig(i, {'fg': COLOUR_LIGHT_TEXT}) # Use standard color


    def on_double_click(self, event=None): # Added event=None for direct calls
        """Handles double-click on listbox item: fetches data and shows Info frame."""
        listbox = self.frames[Tasks].tasks_listbox
        selected_indices = listbox.curselection()
        if not selected_indices:
            return # No item selected

        selected_index = selected_indices[0]
        try:
             task_id = self.task_id_map[selected_index]
        except KeyError:
             messagebox.showerror("Error", "Could not find the selected task ID.")
             return

        selected_task = self.db_manager.get_task_by_id(task_id)

        if not selected_task:
             messagebox.showerror("Error", f"Task with ID {task_id} not found in database.")
             # Refresh listbox in case of inconsistency
             self.fill_listbox(self.db_manager.get_all_tasks())
             return

        # Update StringVars for the Info frame
        self.selected_task_id.set(selected_task.id)
        self.selected_task_desc.set(selected_task.desc)
        self.selected_task_note.set(selected_task.note if selected_task.note else "") # Handle None note
        self.selected_task_date_str.set(selected_task.due_date if selected_task.due_date else "N/A")
        self.selected_task_time_str.set(selected_task.due_time if selected_task.due_time else "N/A")
        self.selected_task_email_str.set(selected_task.email if selected_task.email else "N/A")

        if selected_task.status == 0:
            self.selected_task_status_str.set("Pending")
        else: # Status is 1
            self.selected_task_status_str.set("Done")

        # Switch to Info frame
        self.show_frame(Info)


    def change_status(self, task_id):
        """Marks a task as done."""
        self.db_manager.update_status(task_id)
        self.selected_task_status_str.set("Done")
        # Refresh listbox to show "[Done]" marker and update sorting/color
        self.fill_listbox(self.db_manager.get_all_tasks())
        # Update button states in the Info frame
        self.frames[Info].update_button_states()


    def delete_task(self, task_id):
        """Deletes a task from the database."""
        self.db_manager.delete_task(task_id)


    def show_delete_confirmation(self, task_id):
        """Shows confirmation dialog before deleting a task."""
        # Fetch task description for the message
        task = self.db_manager.get_task_by_id(task_id)
        task_name = task.desc if task else f"Task ID {task_id}"

        yes_no = messagebox.askyesno(
            title="Confirm Deletion",
            message=f"Are you sure you want to delete the task '{task_name}'?\nThis action cannot be undone.",
            icon='warning' # Add warning icon
        )
        if yes_no:
            self.delete_task(task_id)
            task_list = self.db_manager.get_all_tasks()
            self.fill_listbox(task_list)
            self.show_frame(Tasks) # Go back to the main task list


    def edit_task_prep(self):
        """Prepares the AddEdit frame for editing the selected task."""
        frame = self.frames[AddEdit]
        self.add_or_edit.set("Edit Task") # Set the title

        # Get the task details
        frame.task_desc.set(self.selected_task_desc.get())
        frame.task_note_input.delete("1.0", tk.END)
        frame.task_note_input.insert("1.0", self.selected_task_note.get())
        frame.task_email.set(self.selected_task_email_str.get() if self.selected_task_email_str.get() != "N/A" else "")

        # Handle date and time
        has_date = self.selected_task_date_str.get() != "N/A"
        frame.is_date_checked.set(1 if has_date else 0)

        if has_date:
             frame.cal.config(state='normal')
             try:
                 frame.cal.selection_set(self.selected_task_date_str.get())
             except Exception as e:
                 print(f"Error setting calendar date: {e}")
                 frame.cal.selection_set(date.today()) # Fallback

             has_time = self.selected_task_time_str.get() != "N/A"
             frame.is_time_checked.set(1 if has_time else 0)
             frame.time_set_check.config(state='normal') # Enable time checkbox

             if has_time:
                 # Parse HH:MM string and set spinboxes
                 try:
                     time_parts = self.selected_task_time_str.get().split(':')
                     hour = int(time_parts[0])
                     minute = int(time_parts[1])
                     frame.hour_var.set(f"{hour:02d}") # Set with leading zero
                     frame.minute_var.set(f"{minute:02d}") # Set with leading zero
                     # Set spinbox state to allow interaction
                     frame.hour_spinbox.config(state='readonly') # Or 'normal'
                     frame.minute_spinbox.config(state='readonly') # Or 'normal'
                 except (IndexError, ValueError, TypeError) as e:
                     print(f"Error parsing time '{self.selected_task_time_str.get()}': {e}")
                     # Reset to default if parsing fails
                     frame.hour_var.set("00")
                     frame.minute_var.set("00")
                     frame.hour_spinbox.config(state='disabled')
                     frame.minute_spinbox.config(state='disabled')
                     frame.is_time_checked.set(0) # Uncheck if time was invalid
             else:
                 # No time exists, ensure spinboxes are disabled and reset
                 frame.hour_var.set("00")
                 frame.minute_var.set("00")
                 frame.hour_spinbox.config(state='disabled')
                 frame.minute_spinbox.config(state='disabled')

        else:
            # No date, so disable date and time widgets and reset time
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

        # Ensure focus is set
        frame.task_desc_input.focus()


    # edit_task method is removed, logic moved to AddEdit frame's save_task
    # which calls db_manager.update_task directly


    def is_desc_unique(self, new_desc, current_task_id=None):
         """Checks if a description is unique, optionally excluding the current task."""
         tasks = self.db_manager.get_all_tasks()
         for task in tasks:
             # If we are editing (current_task_id is provided), skip check against itself
             if current_task_id is not None and task.id == current_task_id:
                 continue
             # Check if new description matches another task's description (case-insensitive check optional)
             if new_desc.strip().lower() == task.desc.strip().lower():
                 return False # Not unique
         return True # Unique


    # --- Email Reminder Logic ---
    def run_reminders(self):
        """Periodically checks for tasks needing reminders and sends emails."""
        print("---- Reminder thread started ----") # <-- Make sure you see this!
        while not self.stop_reminder_event.is_set():
            try:
                now = datetime.now()
                # --- Added Debug Print ---
                print(f"\n[{now.strftime('%Y-%m-%d %H:%M:%S')}] Reminder check running...")
                tasks_to_check = self.db_manager.get_tasks_for_reminder()

                # --- Added Debug Print ---
                if not tasks_to_check:
                    print("  - No tasks found needing reminders (pending, with date, time, and email).")
                else:
                     print(f"  - Found {len(tasks_to_check)} potential task(s) for reminder.")


                for task in tasks_to_check:
                    # --- Added Debug Print ---
                    print(f"  - Checking task: ID={task.id}, Desc='{task.desc}', DueDate={task.due_date}, DueTime={task.due_time}, Email={task.email}, Status={task.status}")
                    due_dt = task.due_datetime
                    if due_dt:
                        reminder_time_start = due_dt - timedelta(minutes=REMINDER_WINDOW_MINUTES)
                        is_condition_met = reminder_time_start <= now < due_dt
                        # --- Added Debug Print ---
                        print(f"    - Task {task.id}: Now='{now}', Due='{due_dt}', ReminderStart='{reminder_time_start}'")
                        print(f"    - Condition Met (ReminderStart <= Now < Due): {is_condition_met}")

                        if is_condition_met:
                             print(f"    ======> Sending reminder for task: '{task.desc}' (ID: {task.id}) to {task.email}") # Added marker
                             self.send_reminder_email(task)
                             # TODO: Mark task as reminder sent in DB here to avoid repeats
                    else:
                        # --- Added Debug Print ---
                         print(f"    - Task {task.id}: Could not parse due_datetime (Date: {task.due_date}, Time: {task.due_time}).")


            except Exception as e:
                print(f"!!!!!!!! ERROR in reminder thread loop: {e} !!!!!!!!")
                import traceback
                traceback.print_exc() # Print full traceback

            # Wait before the next check
            # print(f" Reminder check finished. Waiting {REMINDER_CHECK_INTERVAL_SECONDS} seconds...") # Optional: uncomment for more verbose waiting info
            self.stop_reminder_event.wait(REMINDER_CHECK_INTERVAL_SECONDS)

        print("---- Reminder thread stopped ----")


    def send_reminder_email(self, task):
        """Constructs and sends a reminder email for the given task."""
        if not task.email or not EMAIL_SENDER_ADDRESS or not EMAIL_SENDER_PASSWORD:
            print("Email configuration missing, cannot send reminder.")
            return

        msg = EmailMessage()
        msg['Subject'] = f"Task Reminder: {task.desc}"
        msg['From'] = EMAIL_SENDER_ADDRESS
        msg['To'] = task.email

        # Format the due date/time nicely
        due_time_str = task.due_datetime.strftime('%I:%M %p') # e.g., 02:30 PM
        due_date_str = task.due_datetime.strftime('%A, %B %d, %Y') # e.g., Tuesday, May 06, 2025

        body = f"Hi,\n\nThis is a reminder for your task:\n\n"
        body += f"**Task:** {task.desc}\n"
        if task.note:
             body += f"**Note:** {task.note}\n"
        body += f"**Due:** {due_date_str} at {due_time_str}\n\n"
        body += f"Have a productive day!\n"

        msg.set_content(body)

        try:
            # Connect to SMTP server and send email
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls() # Secure the connection
                server.login(EMAIL_SENDER_ADDRESS, EMAIL_SENDER_PASSWORD)
                server.send_message(msg)
            print(f"Reminder email sent successfully to {task.email} for task '{task.desc}'.")
        except smtplib.SMTPAuthenticationError:
             print(f"SMTP Authentication Error: Failed to login for email '{EMAIL_SENDER_ADDRESS}'. Check email/password/app password.")
        except smtplib.SMTPConnectError:
             print(f"SMTP Connect Error: Failed to connect to server '{SMTP_SERVER}:{SMTP_PORT}'.")
        except Exception as e:
            print(f"Failed to send email reminder for task '{task.desc}' to {task.email}: {e}")


    def on_closing(self):
        """Handles application closing sequence."""
        print("Closing application...")
        # Signal the reminder thread to stop
        self.stop_reminder_event.set()
        # Wait briefly for the thread to potentially finish its current cycle
        # self.reminder_thread.join(timeout=1.0) # Optional: wait for thread exit
        # Close the database connection
        if self.db_manager:
            self.db_manager.close()
            print("Database connection closed.")
        # Destroy the Tkinter window
        self.destroy()
        print("Application closed.")


# --- Main Execution ---
if __name__ == "__main__":
    try:
        app = TaskManager()
        app.mainloop()
    except Exception as e: # Catch broader exceptions during init
        import traceback
        print("An error occurred during application startup:")
        traceback.print_exc()
        input("Press Enter to exit...")