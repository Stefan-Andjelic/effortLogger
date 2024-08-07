import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from datetime import datetime

def resource_path(relative_path):
    """ Get the absolute path to the resource, works for PyInstaller. """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Predefined categories for "Category" dropdown list
CATEGORIES = ["Software Architecture", "Machine Learning + AI", "Web Development", "Database Architecture", "Data Science", "Cybersecurity", "Networking", "Cloud Computing", "DevOps", "History", "Other"]

def update_stopwatch():
    if running:
        global elapsed_time
        elapsed_time += 1
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        stopwatch_label.config(text=f"{minutes:02}:{seconds:02}")
        root.after(1000, update_stopwatch)

def start_session():
    global running, start_time, category, objectives
    category = category_combobox.get()
    objectives = objectives_text.get("1.0", tk.END).strip()
    if not category or not objectives:
        messagebox.showerror("Error", "Please fill in all fields.")
        return
    running = True
    start_time = datetime.now()
    # Disable all input fields and the start button
    category_combobox.config(state=tk.DISABLED)
    objectives_text.config(state=tk.DISABLED)
    start_button.config(state=tk.DISABLED)
    # Enable the end button
    end_button.config(state=tk.NORMAL)
    update_stopwatch()

# Function to end the session
def end_session():
    global running, end_time
    running = False
    end_time = datetime.now()
    open_prompt("Key Takeaways", key_takeaways_callback)

# Function to finalize the session
def finalize_session():
    global key_takeaways, challenges
    open_prompt("Challenges/Questions", challenges_callback)

def write_to_google_sheet():
    global category, objectives, key_takeaways, challenges, elapsed_time, start_time, end_time
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_path = resource_path("effortlogger-431505-ee70fd600b69.json")
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
        client = gspread.authorize(creds)

        print("Accessing Google Sheet...")
        sheet = client.open("Effort Logger").worksheet("Logger")
        print(f"Successfully accessed Google Sheet: {sheet.title}")

        # Format start and end times
        start_time_str = start_time.strftime("%I:%M:%S %p")
        end_time_str = end_time.strftime("%I:%M:%S %p")

        # Calculate total time
        total_time = end_time - start_time
        total_seconds = int(total_time.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        total_time_str = f"{hours}:{minutes:02}:{seconds:02}"

        # Format date as MM/DD/YYYY
        date_str = start_time.strftime("%m/%d/%Y")
        
        # Prepare the data to be written
        session_data = [
            date_str, 
            start_time_str, 
            end_time_str, 
            total_time_str,
            category, 
            objectives, 
            key_takeaways, 
            challenges
        ]

        print(f"Prepared session data: {session_data}")

        sheet.append_row(session_data)
        print("Test data written successfully.")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while writing to the Google Sheet: {e}")

def open_prompt(title, callback):
    prompt = tk.Toplevel(root)
    prompt.title(title)
    tk.Label(prompt, text=title).pack()
    text_widget = tk.Text(prompt, height=10, width=50)
    text_widget.pack()
    tk.Button(prompt, text="Submit", command=lambda: callback(prompt, text_widget)).pack()
    prompt.grab_set()

def key_takeaways_callback(prompt, text_widget):
    global key_takeaways
    key_takeaways = text_widget.get("1.0", tk.END).strip()
    prompt.destroy()
    finalize_session()

def challenges_callback(prompt, text_widget):
    global challenges
    challenges = text_widget.get("1.0", tk.END).strip()
    prompt.destroy()
    write_to_google_sheet()
    messagebox.showinfo("Session Ended", "Your session has been logged.")
    root.quit()

def exit_application():
    if messagebox.askokcancel("Exit", "Do you really want to exit?"):
        root.quit()

# Create the main window
root = tk.Tk()
root.title("EffortLogger")
root.attributes('-fullscreen', True)

# Category Form
tk.Label(root, text="What will I focus on this session?").pack()
category_combobox = ttk.Combobox(root, values=CATEGORIES)
category_combobox.pack()

# Objectives Form
tk.Label(root, text="What are my objectives for this session?").pack()
objectives_text = tk.Text(root, width=50)
objectives_text.pack()

# Start Button
start_button = tk.Button(root, text="Start", command=start_session)
start_button.pack()

# Stopwatch Label
stopwatch_label = tk.Label(root, text="00:00", font=("Helvetica", 32))
stopwatch_label.pack()

# End Button
end_button = tk.Button(root, text="End", command=end_session, state=tk.DISABLED)
end_button.pack()

# Key Takeaways form (initially hidden)
key_takeaways_label = tk.Label(root, text="What are the key takeaways?")
key_takeaways_text = tk.Text(root, height=5, width=50)

# Challenges form (initially hidden)
challenges_label = tk.Label(root, text="Any challenges/questions?")
challenges_text = tk.Text(root, height=5, width=50)

# Finalize Button (initially hidden)
finalize_button = tk.Button(root, text="Finalize", command=finalize_session)

# Exit Button
exit_button = tk.Button(root, text="Exit", command=exit_application)
exit_button.pack()

# Global Variables
running = False
elapsed_time = 0
category = ""
objectives = ""
key_takeaways = ""
challenges = ""
start_time = None
end_time = None

root.mainloop()