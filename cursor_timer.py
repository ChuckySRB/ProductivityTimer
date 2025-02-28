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
        
        # Define color scheme
        self.colors = {
            'bg': '#f0f2f5',           # Light grayish blue background
            'primary': '#1a73e8',      # Google blue
            'secondary': '#ffffff',     # White
            'text': '#202124',         # Dark gray text
            'accent': '#ea4335'        # Red accent
        }
        
        # Configure root window background
        self.root.configure(bg=self.colors['bg'])
        
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
    
    def process_date_input(self, date_str):
        """Convert date string to datetime.date object.
        Handles both YYYY-MM-DD format and relative days (0, -1, -2, etc.)"""
        try:
            # Try to parse as an integer for relative days
            days_ago = int(date_str)
            return (datetime.datetime.now() + datetime.timedelta(days=days_ago)).date()
        except ValueError:
            # If not an integer, try to parse as YYYY-MM-DD
            return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    
    def setup_gui(self):
        # Configure style for ttk widgets
        style = ttk.Style()
        style.configure('TCombobox', 
                       fieldbackground=self.colors['secondary'],
                       background=self.colors['primary'])
        
        # Timer display
        self.time_label = tk.Label(
            self.root,
            text="00:00:00",
            font=("Arial", 30, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['primary']
        )
        self.time_label.pack(pady=20)
        
        # Start/Stop button
        self.timer_button = tk.Button(
            self.root,
            text="Start",
            command=self.toggle_timer,
            bg=self.colors['primary'],
            fg=self.colors['secondary'],
            font=("Arial", 12, "bold"),
            relief='flat',
            padx=20,
            pady=5
        )
        self.timer_button.pack(pady=10)
        
        # Category selection
        tk.Label(
            self.root,
            text="Select Activity:",
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=("Arial", 10)
        ).pack(pady=5)
        
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(
            self.root,
            textvariable=self.category_var,
            values=self.categories,
            width=25
        )
        self.category_dropdown.pack(pady=5)
        
        # Manual entry section
        tk.Label(
            self.root,
            text="Manual Entry",
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=("Arial", 12, "bold")
        ).pack(pady=10)
        
        # Date entry with placeholder text
        date_frame = tk.Frame(self.root, bg=self.colors['bg'])
        date_frame.pack(pady=5)
        
        tk.Label(
            date_frame,
            text="Date:",
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=5)
        
        self.date_entry = tk.Entry(
            date_frame,
            bg=self.colors['secondary'],
            relief='flat',
            highlightthickness=1,
            highlightbackground=self.colors['primary'],
            width=15
        )
        self.date_entry.insert(0, "0")
        self.date_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            date_frame,
            text="(0=today, -1=yesterday)",
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=("Arial", 8)
        ).pack(side=tk.LEFT, padx=5)
        
        # Time entries frame
        time_frame = tk.Frame(self.root, bg=self.colors['bg'])
        time_frame.pack(pady=5)
        
        self.start_time_entry = tk.Entry(
            time_frame,
            width=10,
            bg=self.colors['secondary'],
            relief='flat',
            highlightthickness=1,
            highlightbackground=self.colors['primary']
        )
        self.start_time_entry.insert(0, "00:00")
        self.start_time_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            time_frame,
            text="to",
            bg=self.colors['bg'],
            fg=self.colors['text']
        ).pack(side=tk.LEFT, padx=5)
        
        self.end_time_entry = tk.Entry(
            time_frame,
            width=10,
            bg=self.colors['secondary'],
            relief='flat',
            highlightthickness=1,
            highlightbackground=self.colors['primary']
        )
        self.end_time_entry.insert(0, "00:00")
        self.end_time_entry.pack(side=tk.LEFT, padx=5)
        
        # Buttons with consistent styling
        button_style = {
            'bg': self.colors['primary'],
            'fg': self.colors['secondary'],
            'font': ("Arial", 10),
            'relief': 'flat',
            'padx': 10,
            'pady': 5
        }
        
        tk.Button(
            self.root,
            text="Add Manual Entry",
            command=self.add_manual_entry,
            **button_style
        ).pack(pady=5)
        
        tk.Button(
            self.root,
            text="Add New Category",
            command=self.add_category,
            **button_style
        ).pack(pady=5)
        
        tk.Button(
            self.root,
            text="View Weekly Stats",
            command=lambda: self.show_stats("week"),
            **button_style
        ).pack(pady=5)
        
        tk.Button(
            self.root,
            text="View Monthly Stats",
            command=lambda: self.show_stats("month"),
            **button_style
        ).pack(pady=5)
    
    def toggle_timer(self):
        if not self.running:
            self.running = True
            self.time_start = datetime.datetime.now()
            self.timer_button.config(
                text="Stop",
                bg=self.colors['accent']  # Change to red when running
            )
            self.update_time()
        else:
            self.running = False
            self.timer_button.config(
                text="Start",
                bg=self.colors['primary']  # Change back to blue when stopped
            )
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
            # Process the date input
            date = self.process_date_input(self.date_entry.get())
            
            # Combine date with time entries
            start_time = f"{date} {self.start_time_entry.get()}"
            end_time = f"{date} {self.end_time_entry.get()}"
            
            # Validate category selection
            if not self.category_var.get():
                messagebox.showwarning("Warning", "Please select an activity category!")
                return
            
            # Parse the datetime strings
            start_dt = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M")
            end_dt = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M")
            
            # Validate time range
            if end_dt <= start_dt:
                messagebox.showerror("Error", "End time must be after start time!")
                return
            
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
            
            # Clear time entries but keep the date
            self.start_time_entry.delete(0, tk.END)
            self.start_time_entry.insert(0, "00:00")
            self.end_time_entry.delete(0, tk.END)
            self.end_time_entry.insert(0, "00:00")
            
        except ValueError as e:
            messagebox.showerror("Error", "Invalid date or time format!\nUse 0 for today, -1 for yesterday, etc.\nOr use YYYY-MM-DD format")
    
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
    
    def get_stats(self, days):
        """Calculate and plot statistics for the last specified number of days."""
        # Define the date range
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days)
        total_time = {}

        # Read and process the log file
        try:
            with open(self.log_file, "r") as f:
                activities = json.load(f)
            
            for activity in activities:
                start = datetime.datetime.fromisoformat(activity['start_time'])
                end = datetime.datetime.fromisoformat(activity['end_time'])
                activity_name = activity['activity']
                
                if start >= start_date and start < end_date:
                    duration = (end - start).total_seconds() / 3600  # Convert to hours
                    total_time[activity_name] = total_time.get(activity_name, 0) + duration
                
        except FileNotFoundError:
            print("No log data found.")
            return

        # Generate statistics and plots
        if total_time:
            # Print total time per activity
            print(f"Total time spent in the last {days} days:")
            for activity, time in sorted(total_time.items()):
                print(f"{activity}: {time:.2f} hours")

            # Create a figure with two subplots side by side
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

            # Prepare data for plotting
            sorted_activities = sorted(total_time.keys())
            times = [total_time[act] for act in sorted_activities]

            # Bar chart on the left subplot
            ax1.bar(sorted_activities, times)
            ax1.set_xlabel("Activity")
            ax1.set_ylabel("Hours")
            ax1.tick_params(axis='x', rotation=45)
            ax1.set_title("Time Distribution (Hours)")

            # Pie chart on the right subplot
            ax2.pie(times, labels=sorted_activities, autopct='%1.1f%%')
            ax2.set_title("Time Distribution (%)")

            # Overall title and layout adjustments
            plt.suptitle(f"Activity Statistics - Last {days} Days")
            plt.tight_layout()
            
            # Save and show the figure
            plt.savefig("stats.png", bbox_inches='tight')
            plt.show()
            print("Statistics plots saved to stats.png")
        else:
            print("No data in the specified range.")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ProductivityTimer()
    app.run() 