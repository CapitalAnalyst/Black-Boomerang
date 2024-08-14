import psutil
import time
import tkinter as tk
from tkinter import ttk, messagebox


class ProcessMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Process Monitor")
        self.root.geometry("400x300")

        # Process name is fixed to 'ScreenshotTool'
        self.process_name = "ScreenshotTool"

        # Display the fixed process name
        # self.process_name_label = tk.Label(root, text=f"Monitoring Process: {self.process_name}")
        # self.process_name_label.pack(pady=10)

        # Start monitoring button
        self.start_button = tk.Button(root, text="Start Monitoring", command=self.start_monitoring)
        self.start_button.pack(pady=10)

        # Stop monitoring button
        self.stop_button = tk.Button(root, text="Stop Monitoring", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        # Output area
        self.output_text = tk.Text(root, height=10, state=tk.DISABLED)
        self.output_text.pack(pady=10)

        self.monitoring = False

    def start_monitoring(self):


        self.processes = [proc for proc in psutil.process_iter(['pid', 'name']) if proc.info['name'] == self.process_name]
        if not self.processes:
            messagebox.showwarning("Process Not Found", f"No processes found with the name '{self.process_name}'.")
            return

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

        total_memory = 0
        total_cpu = 0

        for process in self.processes:
            try:
                total_memory += process.memory_info().rss / (1024 * 1024)  # Convert to MB
                total_cpu += process.cpu_percent(interval=1)
            except psutil.NoSuchProcess:
                self.processes.remove(process)

        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, f"Total Memory Usage: {total_memory:.2f} MB\n")
        self.output_text.insert(tk.END, f"Total CPU Usage: {total_cpu:.2f}%\n")
        self.output_text.config(state=tk.DISABLED)

        if not self.processes:
            messagebox.showinfo("Process Terminated", "All monitored processes have terminated.")
            self.stop_monitoring()
        else:
            self.root.after(2000, self.monitor_processes)  # Update every 2 seconds


if __name__ == "__main__":
    root = tk.Tk()
    app = ProcessMonitorApp(root)
    root.mainloop()
