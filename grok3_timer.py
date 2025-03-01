import datetime
import matplotlib.pyplot as plt
import os

# Constants
CATEGORIES_FILE = "categories.txt"
ACTIVITY_LOG_FILE = "activity_log.csv"
STATS_OUTPUT_FILE = "stats.png"
DEFAULT_CATEGORIES = ["Sleeping", "Coding", "Training", "Other"]

# Function to save categories to a file
def save_categories():
    with open(CATEGORIES_FILE, "w") as f:
        for cat in categories:
            f.write(cat + "\n")

# Load categories from file or use defaults
try:
    with open(CATEGORIES_FILE, "r") as f:
        categories = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    categories = DEFAULT_CATEGORIES

def get_activity():
    """Prompt the user to select or create an activity category."""
    while True:
        print("Select activity:")
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat}")
        print(f"{len(categories)+1}. Create new category")
        choice = input("Enter number: ")
        try:
            index = int(choice) - 1
            if 0 <= index < len(categories):
                return categories[index]
            elif index == len(categories):
                new_cat = input("Enter new category name: ").strip()
                if new_cat.lower() in [c.lower() for c in categories]:
                    print("Category already exists.")
                elif new_cat:
                    categories.append(new_cat)
                    save_categories()
                    print(f"Category '{new_cat}' added.")
                else:
                    print("Category name cannot be empty.")
            elif index == 0:
                return 0
            else:
                print("Invalid choice.")
        except ValueError:
            print("Please enter a number.")

def log_session(start, end, activity):
    """Log the session details to a CSV file."""
    with open(ACTIVITY_LOG_FILE, "a") as f:
        f.write(f"{start.strftime('%Y-%m-%d %H:%M:%S')},{end.strftime('%Y-%m-%d %H:%M:%S')},{activity}\n")

def get_stats(days):
    """Calculate and plot statistics for the last specified number of days."""
    # Define the date range
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=days)
    total_time = {}

    # Read and process the log file
    try:
        with open(ACTIVITY_LOG_FILE, "r") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) != 3:
                    continue
                start_str, end_str, activity = parts
                try:
                    start = datetime.datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
                    end = datetime.datetime.strptime(end_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    continue
                if start >= start_date and start < end_date:
                    duration = (end - start).total_seconds() / 3600  # Convert to hours
                    total_time[activity] = total_time.get(activity, 0) + duration
    except FileNotFoundError:
        print("No log data found.")
        return

    # Generate statistics and plots
    if total_time:
        # Print total time per activity
        print(f"Total time spent in the last {days} days:")
        for activity, time in sorted(total_time.items()):
            print(f"{activity}: {time:.2f} hours")

        # Prepare data for plotting
        sorted_activities = sorted(total_time.keys())
        times = [total_time[act] for act in sorted_activities]

        # Create a figure with two subplots side by side
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

        # Bar chart on the left subplot
        ax1.bar(sorted_activities, times)
        ax1.set_xlabel("Activity")
        ax1.set_ylabel("Hours")
        ax1.set_title("Bar Chart")

        # Pie chart on the right subplot
        ax2.pie(times, labels=sorted_activities, autopct='%1.1f%%')
        ax2.set_title("Pie Chart")

        # Overall title for the figure
        plt.suptitle(f"Time spent in the last {days} days")
        
        # Save the figure
        plt.savefig(STATS_OUTPUT_FILE)
        print(f"Statistics plots saved to {STATS_OUTPUT_FILE}")
    else:
        print("No data in the specified range.")


def main():
    """Main application loop."""
    is_running = False
    print("Welcome to the Activity Stopwatch App.")
    print("\nAvailable commands:")
    print("  start  - Begin a new activity session")
    print("  stop   - End the current session")
    print("  add    - Manually add a past activity")
    print("  stats  - View activity statistics")
    print("  quit   - Exit the application\n")

    while True:
        try:
            command = input("> ").strip().lower()
            if command == 'start':
                if not is_running:
                    start_time = datetime.datetime.now()
                    is_running = True
                    print("Session started.")
                else:
                    print("Session already running.")
            elif command == 'stop':
                if is_running:
                    end_time = datetime.datetime.now()
                    is_running = False
                    duration = (end_time - start_time).total_seconds() / 3600
                    print(f"Session ended. Duration: {duration:.2f} hours")
                    activity = get_activity()
                    if activity != 0:
                        log_session(start_time, end_time, activity)
                    else:
                        print("Activity cancelled.")
                else:
                    print("No session is running.")
            elif command == 'add':
                print("For manual addition, enter times as 'offset HH:MM', where offset is 0 for today, -1 for yesterday, etc.")
                while True:
                    start_input = input("Start time (offset HH:MM): ")
                    try:
                        start_offset_str, start_time_str = start_input.split()
                        start_offset = int(start_offset_str)
                        start_time = datetime.datetime.strptime(start_time_str, "%H:%M").time()
                        start_date = datetime.date.today() + datetime.timedelta(days=start_offset)
                        start_datetime = datetime.datetime.combine(start_date, start_time)
                        break
                    except ValueError:
                        print("Invalid start time. Please use 'offset HH:MM' format.")

                while True:
                    end_input = input("End time (offset HH:MM): ")
                    try:
                        end_offset_str, end_time_str = end_input.split()
                        end_offset = int(end_offset_str)
                        end_time = datetime.datetime.strptime(end_time_str, "%H:%M").time()
                        end_date = datetime.date.today() + datetime.timedelta(days=end_offset)
                        end_datetime = datetime.datetime.combine(end_date, end_time)
                        break
                    except ValueError:
                        print("Invalid end time. Please use 'offset HH:MM' format.")

                if start_datetime < end_datetime:
                    activity = get_activity()
                    log_session(start_datetime, end_datetime, activity)
                    print("Session added successfully.")
                else:
                    print("Start time must be before end time. Please try again.")
            elif command == 'stats':
                days = int(input("Enter number of days: "))
                get_stats(days)
                # open the stats.png file
                os.startfile(STATS_OUTPUT_FILE)
            elif command == 'quit':
                print("Goodbye!")
                break
            elif command == 'help':
                print("\nAvailable commands:")
                print("  start  - Begin a new activity session")
                print("  stop   - End the current session")
                print("  add    - Manually add a past activity")
                print("  stats  - View activity statistics")
                print("  quit   - Exit the application\n")
            else:
                print("Invalid command")
        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    OUTPUT_DIR = "outputs"
    ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_DIR)
    CATEGORIES_FILE = os.path.join(ROOT_DIR, "categories.txt")
    ACTIVITY_LOG_FILE = os.path.join(ROOT_DIR, "activity_log.csv")
    STATS_OUTPUT_FILE = os.path.join(ROOT_DIR, "stats.png")
    main()