import datetime
import matplotlib.pyplot as plt

# Function to save categories to a file
def save_categories():
    with open("categories.txt", "w") as f:
        for cat in categories:
            f.write(cat + "\n")

# Load categories from file or use defaults
try:
    with open("categories.txt", "r") as f:
        categories = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    categories = ["Sleeping", "Coding", "Training", "Other"]

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
                if categories[index] == "Other":
                    return input("Enter activity name: ")
                else:
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
            else:
                print("Invalid choice.")
        except ValueError:
            print("Please enter a number.")

def log_session(start, end, activity):
    """Log the session details to a CSV file."""
    with open("activity_log.csv", "a") as f:
        f.write(f"{start.strftime('%Y-%m-%d %H:%M:%S')},{end.strftime('%Y-%m-%d %H:%M:%S')},{activity}\n")

def get_stats(days):
    """Calculate and plot statistics for the last specified number of days."""
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=days)
    total_time = {}
    
    try:
        with open("activity_log.csv", "r") as f:
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
                    duration = (end - start).total_seconds() / 3600
                    total_time[activity] = total_time.get(activity, 0) + duration
    except FileNotFoundError:
        print("No log data found.")
        return
    
    if total_time:
        print(f"Total time spent in the last {days} days:")
        for activity, time in sorted(total_time.items()):
            print(f"{activity}: {time:.2f} hours")
        sorted_activities = sorted(total_time.keys())
        times = [total_time[act] for act in sorted_activities]
        plt.bar(sorted_activities, times)
        plt.xlabel("Activity")
        plt.ylabel("Hours")
        plt.title(f"Time spent in the last {days} days")
        plt.savefig("stats.png")
        print("Statistics plot saved to stats.png")
    else:
        print("No data in the specified range.")

def main():
    """Main application loop."""
    is_running = False
    print("Welcome to the Activity Stopwatch App.")
    print("Type 'start' to begin, 'stop' to end, 'add' to manually add, 'stats' for stats, 'quit' to exit.")
    
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
                    log_session(start_time, end_time, activity)
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
            elif command == 'quit':
                print("Goodbye!")
                break
            else:
                print("Invalid command")
        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()