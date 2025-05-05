# frames/__init__.py
# This file makes the 'frames' directory act as a Python package.
# It allows us to easily import the frame classes using 'from frames import ...'

# Import the frame classes to make them available directly when importing 'frames'
from frames.tasks import Tasks
from frames.add_edit import AddEdit
from frames.info import Info

# You could define an __all__ variable here to control what '*' imports, but it's not strictly necessary for this project.
# __all__ = ["Tasks", "AddEdit", "Info"]