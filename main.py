import pyautogui
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from datetime import datetime

# Initialize save_folder as None
save_folder = None

def set_save_folder():
    global save_folder
    # Open folder select dialog
    save_folder = filedialog.askdirectory()
    if save_folder:
        messagebox.showinfo("Save Folder Set", f"Save folder set to {save_folder}")
    else:
        messagebox.showwarning("Warning", "Save folder not set. Screenshot will not be saved.")

def take_screenshot():
    global save_folder
    if not save_folder:
        messagebox.showwarning("Warning", "Save folder not set. Please set a save folder first.")
        return

    # Generate a unique filename using the current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(save_folder, f"screenshot_{timestamp}.png")

    # Take a screenshot using PyAutoGUI
    screenshot = pyautogui.screenshot()
    screenshot.save(file_path)
    messagebox.showinfo("Screenshot Taken", f"Screenshot saved to {file_path}")

# Create main window
root = tk.Tk()
root.title("Screenshot Tool")

# Set window icon
icon_path = "/Users/sjh/Downloads/icon.ico"  # Replace with your icon path
root.iconbitmap(icon_path)

# Load the button icons

# screenshot_icon = ImageTk.PhotoImage(Image.open("./lcPPc0WAve.jpg").resize((36,36)))

# Create buttons with icons and bind click events
set_folder_button = tk.Button(root, text="Set Save Folder", compound="left", command=set_save_folder)
set_folder_button.pack(pady=10)

screenshot_button = tk.Button(root, text="Take Screenshot", compound="left", command=take_screenshot)
screenshot_button.pack(pady=10)

# Run main loop
root.mainloop()