import tkinter as tk
from tkinter import ttk, messagebox
import json
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

class ProductivityTimer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Productivity Timer")
        self.root.geometry("400x600")
        
        # Initialize variables
        self.running = False
        self.time_start = None
        self.default_categories = ["Sleep", "Work", "Exercise", "Coding", "Other"]
        self.load_categories()
        
        # Create and configure GUI
        self.setup_gui()
        
        # Load or create log file
        self.log_file = "activity_log.json"
        if not Path(self.log_file).exists():
            with open(self.log_file, "w") as f:
                json.dump([], f)
    
    def load_categories(self):
        try:
            with open("categories.json", "r") as f:
                self.categories = json.load(f)
        except FileNotFoundError:
            self.categories = self.default_categories
            with open("categories.json", "w") as f:
                json.dump(self.categories, f)
    
    def save_categories(self):
        with open("categories.json", "w") as f:
            json.dump(self.categories, f)
    
    def setup_gui(self):
        # Timer display
        self.time_label = tk.Label(self.root, text="00:00:00", font=("Arial", 30))
        self.time_label.pack(pady=20)
        
        # Start/Stop button
        self.timer_button = tk.Button(self.root, text="Start", command=self.toggle_timer)
        self.timer_button.pack(pady=10)
        
        # Category selection
        tk.Label(self.root, text="Select Activity:").pack(pady=5)
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(self.root, textvariable=self.category_var, values=self.categories)
        self.category_dropdown.pack(pady=5)
        
        # Manual entry section
        tk.Label(self.root, text="Manual Entry").pack(pady=10)
        
        # Date entry
        self.date_entry = tk.Entry(self.root)
        self.date_entry.insert(0, datetime.datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.pack(pady=5)
        
        # Time entries
        time_frame = tk.Frame(self.root)
        time_frame.pack(pady=5)
        
        self.start_time_entry = tk.Entry(time_frame, width=10)
        self.start_time_entry.insert(0, "00:00")
        self.start_time_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(time_frame, text="to").pack(side=tk.LEFT, padx=5)
        
        self.end_time_entry = tk.Entry(time_frame, width=10)
        self.end_time_entry.insert(0, "00:00")
        self.end_time_entry.pack(side=tk.LEFT, padx=5)
        
        # Add manual entry button
        tk.Button(self.root, text="Add Manual Entry", command=self.add_manual_entry).pack(pady=5)
        
        # Category management
        tk.Button(self.root, text="Add New Category", command=self.add_category).pack(pady=5)
        
        # Statistics buttons
        tk.Button(self.root, text="View Weekly Stats", command=lambda: self.show_stats("week")).pack(pady=5)
        tk.Button(self.root, text="View Monthly Stats", command=lambda: self.show_stats("month")).pack(pady=5)
    
    def toggle_timer(self):
        if not self.running:
            self.running = True
            self.time_start = datetime.datetime.now()
            self.timer_button.config(text="Stop")
            self.update_time()
        else:
            self.running = False
            self.timer_button.config(text="Start")
            self.save_activity()
    
    def update_time(self):
        if self.running:
            elapsed_time = datetime.datetime.now() - self.time_start
            hours, remainder = divmod(int(elapsed_time.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            self.time_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            self.root.after(1000, self.update_time)
    
    def save_activity(self):
        if not self.category_var.get():
            messagebox.showwarning("Warning", "Please select an activity category!")
            return
            
        end_time = datetime.datetime.now()
        activity = {
            "start_time": self.time_start.isoformat(),
            "end_time": end_time.isoformat(),
            "activity": self.category_var.get()
        }
        
        with open(self.log_file, "r") as f:
            activities = json.load(f)
        
        activities.append(activity)
        
        with open(self.log_file, "w") as f:
            json.dump(activities, f)
    
    def add_manual_entry(self):
        try:
            date = self.date_entry.get()
            start_time = f"{date} {self.start_time_entry.get()}"
            end_time = f"{date} {self.end_time_entry.get()}"
            
            start_dt = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M")
            end_dt = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M")
            
            activity = {
                "start_time": start_dt.isoformat(),
                "end_time": end_dt.isoformat(),
                "activity": self.category_var.get()
            }
            
            with open(self.log_file, "r") as f:
                activities = json.load(f)
            
            activities.append(activity)
            
            with open(self.log_file, "w") as f:
                json.dump(activities, f)
                
            messagebox.showinfo("Success", "Manual entry added successfully!")
        except ValueError as e:
            messagebox.showerror("Error", "Invalid date or time format!")
    
    def add_category(self):
        new_category = tk.simpledialog.askstring("New Category", "Enter new category name:")
        if new_category and new_category not in self.categories:
            self.categories.append(new_category)
            self.category_dropdown['values'] = self.categories
            self.save_categories()
    
    def show_stats(self, period):
        with open(self.log_file, "r") as f:
            activities = json.load(f)
        
        if not activities:
            messagebox.showinfo("Info", "No activities recorded yet!")
            return
        
        df = pd.DataFrame(activities)
        df['start_time'] = pd.to_datetime(df['start_time'])
        df['end_time'] = pd.to_datetime(df['end_time'])
        df['duration'] = (df['end_time'] - df['start_time']).dt.total_seconds() / 3600  # Convert to hours
        
        # Filter for the specified period
        now = pd.Timestamp.now()
        if period == "week":
            start_date = now - pd.Timedelta(days=7)
            title = "Last 7 Days Activity Distribution"
        else:  # month
            start_date = now - pd.Timedelta(days=30)
            title = "Last 30 Days Activity Distribution"
        
        df = df[df['start_time'] >= start_date]
        
        # Create pie chart
        plt.figure(figsize=(10, 8))
        activity_totals = df.groupby('activity')['duration'].sum()
        plt.pie(activity_totals, labels=activity_totals.index, autopct='%1.1f%%')
        plt.title(title)
        plt.show()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ProductivityTimer()
    app.run() 