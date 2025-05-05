# frames/tasks.py
# This is the main frame that shows the list of tasks.

import tkinter as tk
from tkinter import ttk
from tkinter import font # For setting custom fonts

class Tasks(ttk.Frame):
    """
    The main Frame class for displaying the list of tasks.
    Contains the Listbox showing tasks and buttons for Add and Exit.
    """
    def __init__(self, parent, controller, show_add_frame, show_info_frame):
        """
        Sets up the Tasks frame.
        Args:
            parent: The parent widget.
            controller: The main App class instance.
            show_add_frame: Function to switch to the Add/Edit frame (for adding).
            show_info_frame: Function to switch to the Info frame (when a task is double-clicked).
        """
        super().__init__(parent)

        # Define font for the listbox items
        listbox_font = font.Font(family="Rockwell", size=16) # Adjusted size

        self["style"] = "Background.TFrame" # Apply background style

        self.controller = controller # Store reference to main app controller

        # Main title label for the app
        task_manager_label = ttk.Label(
            self,
            text="Task Manager",
            style="title.TLabel", # Use the title style defined in app.py
        )
        task_manager_label.grid(row=0, column=0, sticky="w", padx=20, pady=20) # Align top-left

        # Frame to hold the listbox and its scrollbar
        tasks_frame = ttk.Frame(self, height="100") # Height seems arbitrary here, listbox height more important
        tasks_frame.grid(row=1, column=0, sticky="nsew", padx=60, pady=10) # Padding around listbox area

        # Vertical scrollbar for the listbox
        scrollbar = tk.Scrollbar(
            tasks_frame,
            orient="vertical",
        )

        # The Listbox widget to display tasks
        self.tasks_listbox = tk.Listbox(
            tasks_frame,
            width="50", # Width in characters
            yscrollcommand=scrollbar.set, # Link scrollbar to listbox y-view
            font=listbox_font,
            background="#212A3E", # Dark background
            foreground="#fff",    # Light text
            activestyle="none",    # Don't change appearance of selected item (we handle double-click)
            height=15,             # Height in number of rows
            borderwidth=0,         # Remove border
            highlightthickness=0   # Remove focus highlight border
        )
        self.tasks_listbox.grid(row=0, column=0, sticky="nsew") # Fill the tasks_frame area

        # Configure the scrollbar to control the listbox's y-view
        scrollbar.config(command=self.tasks_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns") # Place scrollbar to the right, fill vertically

        # Frame to hold the Add and Exit buttons
        buttons_container = ttk.Frame(self, style="container.TFrame")
        buttons_container.grid(row=2, column=0, sticky="ew") # Below listbox, expand horizontally

        # Configure button container columns to have equal weight (helps spacing)
        buttons_container.columnconfigure((0, 1), weight=1)
        buttons_container.rowconfigure(0, weight=1)

        # Add Task Button
        self.add_button = ttk.Button(
            buttons_container,
            text="Add",
            style="button.TButton",
            # Lambda calls two functions: sets title for Add/Edit frame, then shows it
            command=lambda: [self.change_label_to_add(), show_add_frame()],
        )
        self.add_button.grid(row=0, column=0, sticky="ew", padx=20, pady=20) # Expand E-W

        # Exit Application Button
        self.exit_button = ttk.Button(
            buttons_container,
            text="Exit",
            style="button.TButton",
            command=self.controller.on_closing # Call the controller's closing method
        )
        self.exit_button.grid(row=0, column=1, sticky="ew", padx=20, pady=20) # Expand E-W

        # Bind the Double-Click event (<Double-1>) on the listbox items
        self.tasks_listbox.bind(
            "<Double-1>",
            # Lambda calls controller's method to load task data, then shows Info frame
            lambda event: [controller.on_double_click(event), show_info_frame()],
        )

    def change_label_to_add(self):
        """
        Helper method called before showing the Add/Edit frame for adding.
        It tells the controller to set the title label in that frame to "Add Task".
        """
        self.controller.add_or_edit.set("Add Task")