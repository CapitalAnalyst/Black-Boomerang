import json
import logging
import shutil
import threading
import webbrowser
import datetime
import pyautogui
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import sys

import pandas as pd
from spider.spider import *




save_folder = None
news_urls = []
news_items = []
current_news_index = 0

def get_resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_writable_path(filename):
    """ Determine a writable directory for storing the updated CSV file """
    user_data_dir = os.path.expanduser("~")  # Store in the user's home directory
    writable_path = os.path.join(user_data_dir, "BlackBoomerang", filename)
    os.makedirs(os.path.dirname(writable_path), exist_ok=True)  # Create the directory if it doesn't exist
    return writable_path

def set_save_folder_on_startup():
    global save_folder
    root.withdraw()  # Hide the main window
    save_folder = filedialog.askdirectory(title="Select Save Folder")
    root.deiconify()  # Show the main window after the folder is selected

    if not save_folder:
        messagebox.showwarning("Warning", "Save folder not set. Screenshot will not be saved.")
        root.destroy()

def take_screenshot(event):
    global save_folder
    if not save_folder:
        messagebox.showwarning("Warning", "Save folder not set. Please set a save folder first.")
        return

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(save_folder, f"screenshot_{timestamp}.png")
    screenshot = pyautogui.screenshot()
    screenshot.save(file_path)
    messagebox.showinfo("Screenshot Taken", f"Screenshot saved to {file_path}")

def fetch_news_from_csv(file_path):
    global news_items, news_urls
    try:
        df = pd.read_csv(file_path)
        news_items = []
        news_urls = []

        for index, row in df.iterrows():
            date = row['Date'].replace('\n', ' ').strip()
            content = row['Summary']
            label = row['Final Label']
            url = row['URL']
            news_item = f"Date: {date} Content: {content}  Classified: {label}"
            news_items.append(news_item)
            news_urls.append(url)
    except Exception as e:
        print(f"Failed to fetch news from CSV: {e}")
        news_items = []
        news_urls = []

def open_current_url(event):
    global current_news_index
    if news_urls and current_news_index < len(news_urls):
        webbrowser.open(news_urls[current_news_index])

def update_news_ticker():
    global current_news_index, news_items
    news_text = news_items[current_news_index]

    def scroll_text():
        nonlocal news_text
        global current_news_index
        news_text = news_text[1:]
        news_label.config(text=news_text)

        if len(news_text.strip()) > 0:
            news_label.after(100, scroll_text)
        else:
            current_news_index = (current_news_index + 1) % len(news_items)
            news_label.after(2000, update_news_ticker)

    scroll_text()

def run_scraper_task():
    urls_and_sites = {
        "https://thehackernews.com/": "hackernews",
        "https://www.cyber.gov.au/about-us/view-all-content/news-and-media": "cyber",
        "https://www.afp.gov.au/news-centre": "afp"
    }

    for url, site in urls_and_sites.items():
        html_content = download_html(url)
        if html_content:
            parse_and_save_news(html_content, site)

    # Path to the newly generated CSV
    generated_csv_path = get_writable_path("final_new.csv")


    # Path to the writable final.csv location
    writable_csv_path = get_writable_path("final.csv")



    # Replace the old final.csv with the new one
    shutil.move(generated_csv_path, writable_csv_path)
    print(f"CSV file has been updated: {writable_csv_path}")


    # Schedule the next run in 24 hours
    threading.Timer(86400, run_scraper_task).start()  # 86400 seconds = 24 hours
    csv_file_path = ensure_writable_csv()
    fetch_news_from_csv(csv_file_path)



def start_scraper_in_background():
    # Run scraper task in a background thread
    scraper_thread = threading.Thread(target=run_scraper_task)
    scraper_thread.daemon = False # Ensure thread continues running until completion
    scraper_thread.start()

# Ensure final.csv exists in a writable location
def ensure_writable_csv():
    writable_csv_path = get_writable_path("final.csv")
    if not os.path.exists(writable_csv_path):
        # Copy the bundled final.csv to the writable location
        shutil.copy(get_resource_path("final.csv"), writable_csv_path)
    return writable_csv_path

# Start the scraper in the background
start_scraper_in_background()

root = ttk.Window(themename="superhero")
root.title("BlackBoomerang")

set_save_folder_on_startup()

# Load the CSV from the writable location
csv_file_path = ensure_writable_csv()
fetch_news_from_csv(csv_file_path)

window_width = 70
window_height = 60
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

position_top = screen_height - window_height - 100
position_right = screen_width - window_width - 5

root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
root.resizable(False, False)

top_window = tk.Toplevel()
top_window.overrideredirect(True)
top_window.attributes('-topmost', True)
top_window.geometry(f"{top_window.winfo_screenwidth()}x45+0+0")

news_label = tk.Label(top_window, text="", bg="yellow", font=("Helvetica", 40), anchor='w')
news_label.pack(fill='both')
news_label.bind("<Button-1>", open_current_url)

update_news_ticker()

# Correctly load the image
image_path = get_resource_path("Cyber copy.png")

image = Image.open(image_path).resize((window_width, window_height))
bg_photo = ImageTk.PhotoImage(image)
bg_label = tk.Label(root, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)
bg_label.bind("<Button-1>", take_screenshot)  # Bind screenshot function to image click

root.mainloop()
