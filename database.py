import sqlite3


def create_database():

    connection = sqlite3.connect("campus_maintenance.db")
    cursor = connection.cursor()

    # Complaints table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            complaint_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            department TEXT NOT NULL,
            building TEXT NOT NULL,
            room_no TEXT NOT NULL,
            category TEXT NOT NULL,
            priority TEXT NOT NULL,
            description TEXT NOT NULL,
            date_reported TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    # Maintenance details table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS maintenance_details (
            maintenance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id INTEGER NOT NULL,
            staff_name TEXT NOT NULL,
            work_done TEXT NOT NULL,
            cost REAL,
            maintenance_date TEXT NOT NULL,
            FOREIGN KEY (complaint_id)
            REFERENCES complaints(complaint_id)
        )
    """)

    connection.commit()
    connection.close()

    print("Database created successfully!")


create_database()