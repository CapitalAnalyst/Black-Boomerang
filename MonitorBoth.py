import os
import sys

import psutil
import tkinter as tk
from tkinter import messagebox
from pystray import Icon, MenuItem as item, Menu
from PIL import Image, ImageDraw
import ttkbootstrap as ttk
def get_resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
class AppMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Application Monitor")

        self.root.withdraw()  # Start with the window hidden

        # Setup the tray icon
        self.tray_icon = self.create_tray_icon()
        self.tray_icon.run_detached()

        self.process_names = ["ScreenshotTool", "MonitorMemory"]  # Replace with your actual process names

        # Create labels for each process
        self.status_labels = {}
        self.process_running_status = {}
        for process_name in self.process_names:
            label = ttk.Label(root, text=f"{process_name}: ", font=("Arial", 14))
            label.pack(anchor="w", padx=20, pady=5)
            status_label = ttk.Label(root, text="Not Running", font=("Arial", 12),bootstyle="danger")
            status_label.pack(anchor="w", padx=20)
            self.status_labels[process_name] = status_label
            self.process_running_status[process_name] = False  # Initial status is Not Running

        # Start monitoring button
        self.start_button = ttk.Button(root, text="Start Monitoring", command=self.start_monitoring)
        self.start_button.pack(pady=10)

        # Stop monitoring button
        self.stop_button = ttk.Button(root, text="Stop Monitoring", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        self.monitoring = False

    def create_tray_icon(self):
        image_path = get_resource_path("lcPPc0WAve.png")
        # Create an image for the tray icon



        image = Image.open(image_path)
        # Define the menu for the tray icon
        menu = Menu(
            item('Open Monitor', self.show_window),
            item('Exit', self.quit_app)
        )

        return Icon("App Monitor", image, "Application Monitor", menu)

    def show_window(self, icon=None, item=None):
        self.root.deiconify()  # Show the window

    def quit_app(self, icon=None, item=None):
        self.stop_monitoring()
        self.tray_icon.stop()
        self.root.quit()

    def start_monitoring(self):
        self.monitoring = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.monitor_processes()

    def stop_monitoring(self):
        self.monitoring = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def monitor_processes(self):
        if not self.monitoring:
            return

        for process_name in self.process_names:
            process_running = any(proc.info['name'] == process_name for proc in psutil.process_iter(['name']))
            if process_running:
                if not self.process_running_status[process_name]:  # It was not running previously
                    self.status_labels[process_name].config(text="Running", bootstyle="success")
                    self.process_running_status[process_name] = True  # Update status to running
            else:
                if self.process_running_status[process_name]:  # It was running previously
                    self.status_labels[process_name].config(text="Not Running", bootstyle="danger")
                    self.process_running_status[process_name] = False  # Update status to not running
                    self.notify_process_stopped(process_name)  # Notify that it stopped

        self.root.after(2000, self.monitor_processes)  # Check every 2 seconds

    def notify_process_stopped(self, process_name):
        messagebox.showwarning("Process Stopped", f"The process '{process_name}' has stopped running!")


if __name__ == "__main__":
    root = ttk.Window(themename="lumen")
    app = AppMonitor(root)


    # Set the window size and prevent resizing
    window_width = 400
    window_height = 200
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calculate the position to center the window
    position_top = int(screen_height / 2 - window_height / 2)
    position_right = int(screen_width / 2 - window_width / 2)

    # Set the geometry of the main window
    root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
    root.mainloop()
