print("Hello, World!")
import sqlite3
from datetime import datetime


class TerraTracker:
    def __init__(self, db_name="habit_tracker.db"):
        # Connect to the SQLite database (creates files automatically)
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.setup_database()

    def setup_database(self):
        # Create the habits table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_date TEXT NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                habit_id INTEGER NOT NULL,
                log_date TEXT NOT NULL,
                status INTEGER DEFAULT 1,
                FOREIGN KEY (habit_id) REFERENCES habits(id),
                PRIMARY KEY (habit_id, log_date)
            )
        ''')
        self.conn.commit()

    def add_habit(self, name):
        today = datetime.now().strftime("%Y-%m-%d")
        try:
            self.cursor.execute(
                "INSERT INTO habits (name, created_date) VALUES (?, ?)",
                (name, today)
            )
            self.conn.commit()
            print(f"[+] Habit added: {name}")
        except sqlite3.Error as e:
            print(f"[!] Could not add habit: {e}")

    def log_habit(self, habit_id):
        today = datetime.now().strftime("%Y-%m-%d")

        # Check if habit ID exists in the habits table first
        self.cursor.execute("SELECT id FROM habits WHERE id = ?", (habit_id,))
        habit = self.cursor.fetchone()

        if not habit:
            print(f"[!] Habit ID {habit_id} does not exist!")
            return

        try:
            self.cursor.execute(
                "INSERT INTO logs (habit_id, log_date, status) VALUES (?, ?, 1)",
                (habit_id, today)
            )
            self.conn.commit()
            print(f"[+] Habit ID {habit_id} marked completed for {today}.")
        except sqlite3.IntegrityError:
            print("[!] You already logged this habit today, BOSS.")

    def view_habits(self):
        self.cursor.execute("SELECT id, name, created_date FROM habits ORDER BY id")
        habits = self.cursor.fetchall()
        if not habits:
            print("[-] No habits found. Add one first.")
            return
        print("\n--- YOUR ACTIVE HABITS ---")
        for habit in habits:
            print(f"id: {habit[0]} | Name: {habit[1]} | Created: {habit[2]}")
        print("-" * 26)

    def close(self):
        self.conn.close()


if __name__ == "__main__":
    tracker = TerraTracker()

    while True:
        print("\n1. View Habits")
        print("2. Add Habit")
        print("3. Log Habit Today")
        print("4. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            tracker.view_habits()
        elif choice == "2":
            habit_name = input("Enter the name of the habit: ").strip()
            if habit_name:
                tracker.add_habit(habit_name)
        elif choice == "3":
            tracker.view_habits()
            try:
                h_id = int(input("Enter the habit ID to log: ").strip())
                tracker.log_habit(h_id)
            except ValueError:
                print("[!] Invalid habit ID. Please enter a number.")
        elif choice == "4":
            tracker.close()
            print("Exiting the Habit Tracker. Goodbye!")
            break
        else:
            print("[!] Invalid choice. Please try again.")