import sqlite3
import time
import os

DB_FILE = 'company_database.db'

def clear_screen():
    # 'cls' is the command to clear the terminal in Windows
    os.system('cls')

def monitor_database():
    while True:
        clear_screen()
        print("=========================================")
        print("   LIVE ENTERPRISE DATABASE MONITOR      ")
        print("=========================================\n")
        
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.execute('SELECT * FROM records ORDER BY rowid DESC LIMIT 10')
                rows = cursor.fetchall()
                
                if not rows:
                    print("Database is currently empty. Waiting for payloads...")
                else:
                    for row in rows:
                        print(f"ID: {row[0]}")
                        print(f"USER: {row[1]}")
                        print(f"DATA: {row[2]}")
                        print("-" * 40)
                        
        except sqlite3.OperationalError:
            print("Waiting for database initialization...")
            
        # Refreshes every 1.5 seconds
        time.sleep(1.5)

if __name__ == '__main__':
    monitor_database()
