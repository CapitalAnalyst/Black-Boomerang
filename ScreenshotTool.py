import json

import pyautogui
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from datetime import datetime

import requests
# Initialize save_folder as None
from ttkbootstrap.icons import Icon

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


def fetch_news():
    global news_text
    api_key = 'f12c1b6fd1c8fe928b130807209b7a1c'  # 请替换为您的API密钥
    url = f"https://gnews.io/api/v4/top-headlines?token={api_key}&lang=en&country=us"

    try:
        response = requests.get(url)
        data = response.json()
        headlines = [article['title'] for article in data['articles']]
        # 将所有标题合并为一个长字符串，每条新闻之间用空格分隔
        news_text = ' *** '.join(headlines)  # 使用特殊字符分隔每条新闻
    except Exception as e:
        print(f"Failed to fetch news: {e}")
        news_text = "Failed to fetch news, check your internet connection or API key."
    finally:
        # 每4分钟更新一次新闻
        root.after(240000, fetch_news)

def update_news_ticker():
    global news_text
    # news_text = fetch_news()
    # Move the first character to the end to create the scrolling effect
    news_text = news_text[1:] + news_text[0]
    # Update the label text
    news_label.config(text=news_text)
    # Schedule the function to run again after a delay
    news_label.after(100, update_news_ticker)

# Create main window
root = ttk.Window(themename="superhero")
root.title("BlackBoomerang")




# Set the window size and prevent resizing
window_width = 400
window_height = 300
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Calculate the position to center the window
position_top = int(screen_height / 2 - window_height / 2)
position_right = int(screen_width / 2 - window_width / 2)


# Set the geometry of the main window
root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
# root.resizable(False, False)  # Disable resizing
# Create a top-level window
top_window = tk.Toplevel()
top_window.overrideredirect(True)  # Remove window decorations (title bar, borders)
top_window.attributes('-topmost', True)  # Keep the window on top
top_window.geometry(f"{top_window.winfo_screenwidth()}x45+0+0")  # Set window size and position

# Add a message ticker to the top-level window
news_text = "Breaking News: Global markets experienced significant volatility today as investors reacted to the latest economic data. The U.S. Federal Reserve announced a further increase in interest rates, citing concerns over persistent inflation. In other news, a major breakthrough in renewable energy was announced as scientists successfully tested a new type of solar panel that could significantly reduce the cost of green energy. Meanwhile, international tensions are rising as multiple countries engage in diplomatic talks to address cybersecurity threats. In the world of entertainment, a highly anticipated film broke box office records on its opening weekend, drawing millions of viewers worldwide. Stay tuned for more updates."



news_label = tk.Label(top_window, text=news_text, bg="yellow", font=("Helvetica", 40), anchor='w')
news_label.pack(fill='both')

# Start the news ticker update loo
# fetch_news()
# update_news_ticker()

image = Image.open("Cyber.jpg").resize((window_width,window_height))
bg_photo = ImageTk.PhotoImage(image)
bg_label = tk.Label(root, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)


root.info_image = tk.PhotoImage(data=Icon.info)
# Load the button icons
set_folder_button = ttk.Button(root, text="Set Save Folder",image=root.info_image, compound="left", command=set_save_folder)
set_folder_button.pack(pady=40)
#


screenshot_button = ttk.Button(root,image=root.info_image,text="Take Screenshot", compound="left", command=take_screenshot)
screenshot_button.pack()


# Run main loop
root.mainloop()
