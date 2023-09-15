import os

def get_current_file_name():
    # Get the path to the current script (including the file name)
    current_script_path = os.path.abspath(__file__)

    # Extract the file name from the path
    current_file_name = os.path.basename(current_script_path)

    # Remove the .py extension from the file name
    if current_file_name.endswith('.py'):
        current_file_name = current_file_name[:-3]  # Remove the last 3 characters (.py)

    return current_file_name