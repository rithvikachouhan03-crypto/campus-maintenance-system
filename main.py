import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime


# =========================================================
# DATABASE
# =========================================================

def create_database():

    connection = sqlite3.connect("campus_maintenance.db")
    cursor = connection.cursor()

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


create_database()


# =========================================================
# REFRESH DASHBOARD
# =========================================================

def refresh_dashboard():

    connection = sqlite3.connect("campus_maintenance.db")
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM complaints")
    total = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM complaints
        WHERE status = 'Pending'
    """)
    pending = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM complaints
        WHERE status = 'In Progress'
    """)
    in_progress = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM complaints
        WHERE status = 'Resolved'
    """)
    resolved = cursor.fetchone()[0]

    connection.close()

    total_label.config(text=str(total))
    pending_label.config(text=str(pending))
    progress_label.config(text=str(in_progress))
    resolved_label.config(text=str(resolved))


# =========================================================
# REGISTER COMPLAINT
# =========================================================

def register_complaint():

    student_name = name_entry.get().strip()
    department = department_combo.get().strip()
    building = building_combo.get().strip()
    room_no = room_entry.get().strip()
    category = category_combo.get().strip()
    priority = priority_combo.get().strip()
    description = description_text.get("1.0", tk.END).strip()

    if not student_name:
        messagebox.showwarning(
            "Missing Information",
            "Please enter student name."
        )
        return

    if not department:
        messagebox.showwarning(
            "Missing Information",
            "Please select department."
        )
        return

    if not building:
        messagebox.showwarning(
            "Missing Information",
            "Please select building."
        )
        return

    if not room_no:
        messagebox.showwarning(
            "Missing Information",
            "Please enter room number."
        )
        return

    if not category:
        messagebox.showwarning(
            "Missing Information",
            "Please select complaint category."
        )
        return

    if not priority:
        messagebox.showwarning(
            "Missing Information",
            "Please select priority."
        )
        return

    if not description:
        messagebox.showwarning(
            "Missing Information",
            "Please enter complaint description."
        )
        return

    date_reported = datetime.now().strftime("%Y-%m-%d")

    connection = sqlite3.connect("campus_maintenance.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO complaints
        (
            student_name,
            department,
            building,
            room_no,
            category,
            priority,
            description,
            date_reported,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        student_name,
        department,
        building,
        room_no,
        category,
        priority,
        description,
        date_reported,
        "Pending"
    ))

    complaint_id = cursor.lastrowid

    connection.commit()
    connection.close()

    messagebox.showinfo(
        "Complaint Registered",
        f"Complaint registered successfully!\n\n"
        f"Your Complaint ID is: {complaint_id}"
    )

    clear_form()
    refresh_dashboard()


# =========================================================
# CLEAR FORM
# =========================================================

def clear_form():

    name_entry.delete(0, tk.END)
    department_combo.set("")
    building_combo.set("")
    room_entry.delete(0, tk.END)
    category_combo.set("")
    priority_combo.set("")
    description_text.delete("1.0", tk.END)


# =========================================================
# VIEW ALL COMPLAINTS
# =========================================================

def view_complaints():

    connection = sqlite3.connect("campus_maintenance.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM complaints
        ORDER BY complaint_id DESC
    """)

    complaints = cursor.fetchall()

    connection.close()

    if not complaints:

        messagebox.showinfo(
            "Complaints",
            "No complaints found."
        )

        return

    window = tk.Toplevel(root)

    window.title("All Complaints")
    window.geometry("1100x600")

    tk.Label(
        window,
        text="All Campus Complaints",
        font=("Arial", 18, "bold")
    ).pack(pady=15)

    frame = tk.Frame(window)
    frame.pack(fill="both", expand=True, padx=15, pady=10)

    columns = (
        "ID",
        "Student",
        "Department",
        "Building",
        "Room",
        "Category",
        "Priority",
        "Date",
        "Status"
    )

    tree = ttk.Treeview(
        frame,
        columns=columns,
        show="headings"
    )

    for column in columns:

        tree.heading(
            column,
            text=column
        )

        tree.column(
            column,
            width=100,
            anchor="center"
        )

    tree.column("ID", width=50)
    tree.column("Student", width=130)
    tree.column("Department", width=100)
    tree.column("Description", width=200)

    for complaint in complaints:

        tree.insert(
            "",
            tk.END,
            values=(
                complaint[0],
                complaint[1],
                complaint[2],
                complaint[3],
                complaint[4],
                complaint[5],
                complaint[6],
                complaint[8],
                complaint[9]
            )
        )

    scrollbar = ttk.Scrollbar(
        frame,
        orient="vertical",
        command=tree.yview
    )

    tree.configure(
        yscrollcommand=scrollbar.set
    )

    tree.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )


# =========================================================
# SEARCH COMPLAINT
# =========================================================

def search_complaint():

    complaint_id = search_entry.get().strip()

    if not complaint_id:

        messagebox.showwarning(
            "Missing ID",
            "Please enter a Complaint ID."
        )

        return

    try:

        complaint_id = int(complaint_id)

    except ValueError:

        messagebox.showerror(
            "Invalid ID",
            "Complaint ID must be a number."
        )

        return

    connection = sqlite3.connect("campus_maintenance.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM complaints
        WHERE complaint_id = ?
    """, (complaint_id,))

    complaint = cursor.fetchone()

    connection.close()

    if complaint:

        result = f"""
Complaint ID: {complaint[0]}

Student Name: {complaint[1]}

Department: {complaint[2]}

Building: {complaint[3]}

Room No.: {complaint[4]}

Category: {complaint[5]}

Priority: {complaint[6]}

Description:
{complaint[7]}

Date Reported: {complaint[8]}

Status: {complaint[9]}
"""

        messagebox.showinfo(
            "Complaint Found",
            result
        )

    else:

        messagebox.showerror(
            "Not Found",
            f"No complaint found with ID {complaint_id}."
        )


# =========================================================
# UPDATE STATUS
# =========================================================

def update_status():

    complaint_id = status_id_entry.get().strip()
    new_status = status_combo.get().strip()

    if not complaint_id or not new_status:

        messagebox.showwarning(
            "Missing Information",
            "Please enter Complaint ID and select a status."
        )

        return

    try:

        complaint_id = int(complaint_id)

    except ValueError:

        messagebox.showerror(
            "Invalid ID",
            "Complaint ID must be a number."
        )

        return

    connection = sqlite3.connect("campus_maintenance.db")
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE complaints
        SET status = ?
        WHERE complaint_id = ?
    """, (
        new_status,
        complaint_id
    ))

    connection.commit()

    if cursor.rowcount > 0:

        messagebox.showinfo(
            "Status Updated",
            f"Complaint {complaint_id} "
            f"status updated to {new_status}."
        )

        status_id_entry.delete(0, tk.END)
        status_combo.set("")

        refresh_dashboard()

    else:

        messagebox.showerror(
            "Not Found",
            f"No complaint found with ID {complaint_id}."
        )

    connection.close()


# =========================================================
# ADD MAINTENANCE DETAILS
# =========================================================

def add_maintenance():

    complaint_id = maintenance_id_entry.get().strip()
    staff_name = staff_entry.get().strip()
    work_done = work_entry.get("1.0", tk.END).strip()
    cost = cost_entry.get().strip()

    if not complaint_id:
        messagebox.showwarning(
            "Missing Information",
            "Please enter Complaint ID."
        )
        return

    if not staff_name:
        messagebox.showwarning(
            "Missing Information",
            "Please enter staff name."
        )
        return

    if not work_done:
        messagebox.showwarning(
            "Missing Information",
            "Please describe the work done."
        )
        return

    if not cost:
        messagebox.showwarning(
            "Missing Information",
            "Please enter maintenance cost."
        )
        return

    try:

        complaint_id = int(complaint_id)
        cost = float(cost)

    except ValueError:

        messagebox.showerror(
            "Invalid Information",
            "Complaint ID must be a number and cost must be numeric."
        )

        return

    connection = sqlite3.connect("campus_maintenance.db")
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT complaint_id
        FROM complaints
        WHERE complaint_id = ?
        """,
        (complaint_id,)
    )

    complaint = cursor.fetchone()

    if not complaint:

        connection.close()

        messagebox.showerror(
            "Not Found",
            "No complaint found with this ID."
        )

        return

    maintenance_date = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        INSERT INTO maintenance_details
        (
            complaint_id,
            staff_name,
            work_done,
            cost,
            maintenance_date
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        complaint_id,
        staff_name,
        work_done,
        cost,
        maintenance_date
    ))

    connection.commit()
    connection.close()

    messagebox.showinfo(
        "Maintenance Added",
        "Maintenance details added successfully!"
    )

    maintenance_id_entry.delete(0, tk.END)
    staff_entry.delete(0, tk.END)
    work_entry.delete("1.0", tk.END)
    cost_entry.delete(0, tk.END)


# =========================================================
# MAINTENANCE WINDOW
# =========================================================

def open_maintenance_window():

    global maintenance_id_entry
    global staff_entry
    global work_entry
    global cost_entry

    maintenance_window = tk.Toplevel(root)

    maintenance_window.title(
        "Add Maintenance Details"
    )

    maintenance_window.geometry(
        "550x500"
    )

    tk.Label(
        maintenance_window,
        text="Maintenance Details",
        font=("Arial", 18, "bold")
    ).pack(pady=20)

    frame = tk.Frame(
        maintenance_window
    )

    frame.pack(pady=10)

    tk.Label(
        frame,
        text="Complaint ID:",
        font=("Arial", 11, "bold")
    ).grid(
        row=0,
        column=0,
        padx=10,
        pady=12,
        sticky="e"
    )

    maintenance_id_entry = tk.Entry(
        frame,
        width=30
    )

    maintenance_id_entry.grid(
        row=0,
        column=1,
        padx=10,
        pady=12
    )

    tk.Label(
        frame,
        text="Staff Name:",
        font=("Arial", 11, "bold")
    ).grid(
        row=1,
        column=0,
        padx=10,
        pady=12,
        sticky="e"
    )

    staff_entry = tk.Entry(
        frame,
        width=30
    )

    staff_entry.grid(
        row=1,
        column=1,
        padx=10,
        pady=12
    )

    tk.Label(
        frame,
        text="Work Done:",
        font=("Arial", 11, "bold")
    ).grid(
        row=2,
        column=0,
        padx=10,
        pady=12,
        sticky="ne"
    )

    work_entry = tk.Text(
        frame,
        width=30,
        height=6
    )

    work_entry.grid(
        row=2,
        column=1,
        padx=10,
        pady=12
    )

    tk.Label(
        frame,
        text="Cost:",
        font=("Arial", 11, "bold")
    ).grid(
        row=3,
        column=0,
        padx=10,
        pady=12,
        sticky="e"
    )

    cost_entry = tk.Entry(
        frame,
        width=30
    )

    cost_entry.grid(
        row=3,
        column=1,
        padx=10,
        pady=12
    )

    tk.Button(
        maintenance_window,
        text="ADD MAINTENANCE",
        command=add_maintenance,
        font=("Arial", 11, "bold"),
        padx=20,
        pady=8
    ).pack(pady=20)


# =========================================================
# VIEW MAINTENANCE DETAILS
# =========================================================

def view_maintenance():

    connection = sqlite3.connect(
        "campus_maintenance.db"
    )

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            m.maintenance_id,
            m.complaint_id,
            m.staff_name,
            m.work_done,
            m.cost,
            m.maintenance_date
        FROM maintenance_details m
        ORDER BY m.maintenance_id DESC
    """)

    details = cursor.fetchall()

    connection.close()

    if not details:

        messagebox.showinfo(
            "Maintenance",
            "No maintenance details found."
        )

        return

    window = tk.Toplevel(root)

    window.title(
        "Maintenance Details"
    )

    window.geometry(
        "950x550"
    )

    tk.Label(
        window,
        text="Maintenance Records",
        font=("Arial", 18, "bold")
    ).pack(pady=15)

    frame = tk.Frame(window)
    frame.pack(
        fill="both",
        expand=True,
        padx=15,
        pady=10
    )

    columns = (
        "Maintenance ID",
        "Complaint ID",
        "Staff",
        "Work Done",
        "Cost",
        "Date"
    )

    tree = ttk.Treeview(
        frame,
        columns=columns,
        show="headings"
    )

    for column in columns:

        tree.heading(
            column,
            text=column
        )

        tree.column(
            column,
            width=130,
            anchor="center"
        )

    tree.column(
        "Work Done",
        width=300
    )

    for detail in details:

        tree.insert(
            "",
            tk.END,
            values=detail
        )

    scrollbar = ttk.Scrollbar(
        frame,
        orient="vertical",
        command=tree.yview
    )

    tree.configure(
        yscrollcommand=scrollbar.set
    )

    tree.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )


# =========================================================
# GENERATE REPORT USING PANDAS
# =========================================================

def generate_report():

    connection = sqlite3.connect(
        "campus_maintenance.db"
    )

    df = pd.read_sql_query(
        "SELECT * FROM complaints",
        connection
    )

    connection.close()

    if df.empty:

        messagebox.showinfo(
            "Report",
            "No complaints available to generate report."
        )

        return

    total = len(df)

    pending = len(
        df[df["status"] == "Pending"]
    )

    in_progress = len(
        df[df["status"] == "In Progress"]
    )

    resolved = len(
        df[df["status"] == "Resolved"]
    )

    high_priority = len(
        df[df["priority"] == "High"]
    )

    medium_priority = len(
        df[df["priority"] == "Medium"]
    )

    low_priority = len(
        df[df["priority"] == "Low"]
    )

    report = f"""
CAMPUS MAINTENANCE REPORT
================================

Total Complaints: {total}

STATUS SUMMARY
--------------------------------
Pending: {pending}
In Progress: {in_progress}
Resolved: {resolved}

PRIORITY SUMMARY
--------------------------------
High Priority: {high_priority}
Medium Priority: {medium_priority}
Low Priority: {low_priority}

================================
"""

    messagebox.showinfo(
        "Maintenance Report",
        report
    )


# =========================================================
# STATUS CHART
# =========================================================

def show_status_chart():

    connection = sqlite3.connect(
        "campus_maintenance.db"
    )

    df = pd.read_sql_query(
        "SELECT * FROM complaints",
        connection
    )

    connection.close()

    if df.empty:

        messagebox.showinfo(
            "Chart",
            "No complaints available to create chart."
        )

        return

    pending = len(
        df[df["status"] == "Pending"]
    )

    in_progress = len(
        df[df["status"] == "In Progress"]
    )

    resolved = len(
        df[df["status"] == "Resolved"]
    )

    statuses = [
        "Pending",
        "In Progress",
        "Resolved"
    ]

    counts = [
        pending,
        in_progress,
        resolved
    ]

    plt.figure(
        figsize=(8, 5)
    )

    plt.bar(
        statuses,
        counts
    )

    plt.title(
        "Complaint Status Report"
    )

    plt.xlabel(
        "Status"
    )

    plt.ylabel(
        "Number of Complaints"
    )

    plt.tight_layout()

    plt.show()


# =========================================================
# CATEGORY CHART
# =========================================================

def show_category_chart():

    connection = sqlite3.connect(
        "campus_maintenance.db"
    )

    df = pd.read_sql_query(
        "SELECT * FROM complaints",
        connection
    )

    connection.close()

    if df.empty:

        messagebox.showinfo(
            "Chart",
            "No complaints available to create chart."
        )

        return

    category_counts = df[
        "category"
    ].value_counts()

    plt.figure(
        figsize=(9, 5)
    )

    plt.bar(
        category_counts.index,
        category_counts.values
    )

    plt.title(
        "Complaints by Category"
    )

    plt.xlabel(
        "Category"
    )

    plt.ylabel(
        "Number of Complaints"
    )

    plt.xticks(
        rotation=30
    )

    plt.tight_layout()

    plt.show()


# =========================================================
# MAIN WINDOW
# =========================================================

root = tk.Tk()

root.title(
    "Campus Maintenance Complaint & Tracking System"
)

root.geometry(
    "1100x800"
)

root.minsize(
    950,
    700
)


# =========================================================
# TITLE
# =========================================================

title_label = tk.Label(
    root,
    text="CAMPUS MAINTENANCE",
    font=("Arial", 24, "bold")
)

title_label.pack(
    pady=(15, 2)
)

subtitle_label = tk.Label(
    root,
    text="Complaint & Tracking System",
    font=("Arial", 14)
)

subtitle_label.pack(
    pady=(0, 15)
)


# =========================================================
# DASHBOARD
# =========================================================

dashboard_frame = tk.Frame(
    root
)

dashboard_frame.pack(
    pady=5
)


# Total

total_box = tk.Frame(
    dashboard_frame,
    relief="solid",
    borderwidth=1,
    padx=30,
    pady=10
)

total_box.grid(
    row=0,
    column=0,
    padx=8
)

tk.Label(
    total_box,
    text="TOTAL",
    font=("Arial", 10, "bold")
).pack()

total_label = tk.Label(
    total_box,
    text="0",
    font=("Arial", 20, "bold")
)

total_label.pack()


# Pending

pending_box = tk.Frame(
    dashboard_frame,
    relief="solid",
    borderwidth=1,
    padx=30,
    pady=10
)

pending_box.grid(
    row=0,
    column=1,
    padx=8
)

tk.Label(
    pending_box,
    text="PENDING",
    font=("Arial", 10, "bold")
).pack()

pending_label = tk.Label(
    pending_box,
    text="0",
    font=("Arial", 20, "bold")
)

pending_label.pack()


# In Progress

progress_box = tk.Frame(
    dashboard_frame,
    relief="solid",
    borderwidth=1,
    padx=25,
    pady=10
)

progress_box.grid(
    row=0,
    column=2,
    padx=8
)

tk.Label(
    progress_box,
    text="IN PROGRESS",
    font=("Arial", 10, "bold")
).pack()

progress_label = tk.Label(
    progress_box,
    text="0",
    font=("Arial", 20, "bold")
)

progress_label.pack()


# Resolved

resolved_box = tk.Frame(
    dashboard_frame,
    relief="solid",
    borderwidth=1,
    padx=30,
    pady=10
)

resolved_box.grid(
    row=0,
    column=3,
    padx=8
)

tk.Label(
    resolved_box,
    text="RESOLVED",
    font=("Arial", 10, "bold")
).pack()

resolved_label = tk.Label(
    resolved_box,
    text="0",
    font=("Arial", 20, "bold")
)

resolved_label.pack()


# =========================================================
# REGISTRATION FORM
# =========================================================

form_container = tk.Frame(
    root
)

form_container.pack(
    pady=10
)

form_frame = tk.LabelFrame(
    form_container,
    text="Register New Complaint",
    font=("Arial", 12, "bold"),
    padx=20,
    pady=15
)

form_frame.pack()


# Student Name

tk.Label(
    form_frame,
    text="Student Name:",
    font=("Arial", 10, "bold")
).grid(
    row=0,
    column=0,
    padx=10,
    pady=7,
    sticky="e"
)

name_entry = tk.Entry(
    form_frame,
    width=28
)

name_entry.grid(
    row=0,
    column=1,
    padx=10,
    pady=7
)


# Department

tk.Label(
    form_frame,
    text="Department:",
    font=("Arial", 10, "bold")
).grid(
    row=0,
    column=2,
    padx=10,
    pady=7,
    sticky="e"
)

department_combo = ttk.Combobox(
    form_frame,
    values=[
        "AI",
        "CSE",
        "Cyber Security",
        "IT",
        "ECE",
        "Mechanical",
        "Civil"
    ],
    width=25,
    state="readonly"
)

department_combo.grid(
    row=0,
    column=3,
    padx=10,
    pady=7
)


# Building

tk.Label(
    form_frame,
    text="Building:",
    font=("Arial", 10, "bold")
).grid(
    row=1,
    column=0,
    padx=10,
    pady=7,
    sticky="e"
)

building_combo = ttk.Combobox(
    form_frame,
    values=[
        "Block A",
        "Block B",
        "Block C",
        "Block D",
        "Block E",
        "Block F"
    ],
    width=25,
    state="readonly"
)

building_combo.grid(
    row=1,
    column=1,
    padx=10,
    pady=7
)


# Room

tk.Label(
    form_frame,
    text="Room No.:",
    font=("Arial", 10, "bold")
).grid(
    row=1,
    column=2,
    padx=10,
    pady=7,
    sticky="e"
)

room_entry = tk.Entry(
    form_frame,
    width=28
)

room_entry.grid(
    row=1,
    column=3,
    padx=10,
    pady=7
)


# Category

tk.Label(
    form_frame,
    text="Category:",
    font=("Arial", 10, "bold")
).grid(
    row=2,
    column=0,
    padx=10,
    pady=7,
    sticky="e"
)

category_combo = ttk.Combobox(
    form_frame,
    values=[
        "Electrical",
        "Plumbing",
        "Furniture",
        "Cleaning",
        "Internet",
        "Air Conditioning",
        "Other"
    ],
    width=25,
    state="readonly"
)

category_combo.grid(
    row=2,
    column=1,
    padx=10,
    pady=7
)


# Priority

tk.Label(
    form_frame,
    text="Priority:",
    font=("Arial", 10, "bold")
).grid(
    row=2,
    column=2,
    padx=10,
    pady=7,
    sticky="e"
)

priority_combo = ttk.Combobox(
    form_frame,
    values=[
        "Low",
        "Medium",
        "High"
    ],
    width=25,
    state="readonly"
)

priority_combo.grid(
    row=2,
    column=3,
    padx=10,
    pady=7
)


# Description

tk.Label(
    form_frame,
    text="Description:",
    font=("Arial", 10, "bold")
).grid(
    row=3,
    column=0,
    padx=10,
    pady=7,
    sticky="ne"
)

description_text = tk.Text(
    form_frame,
    width=28,
    height=4
)

description_text.grid(
    row=3,
    column=1,
    padx=10,
    pady=7
)

tk.Label(
    form_frame,
    text="Example: Fan is not working",
    font=("Arial", 9)
).grid(
    row=3,
    column=2,
    columnspan=2,
    padx=10,
    pady=7
)


# =========================================================
# REGISTER / CLEAR BUTTONS
# =========================================================

button_frame = tk.Frame(
    root
)

button_frame.pack(
    pady=8
)

register_button = tk.Button(
    button_frame,
    text="REGISTER COMPLAINT",
    command=register_complaint,
    font=("Arial", 10, "bold"),
    padx=18,
    pady=8
)

register_button.grid(
    row=0,
    column=0,
    padx=5
)

clear_button = tk.Button(
    button_frame,
    text="CLEAR FORM",
    command=clear_form,
    font=("Arial", 10, "bold"),
    padx=18,
    pady=8
)

clear_button.grid(
    row=0,
    column=1,
    padx=5
)

view_button = tk.Button(
    button_frame,
    text="VIEW ALL COMPLAINTS",
    command=view_complaints,
    font=("Arial", 10, "bold"),
    padx=18,
    pady=8
)

view_button.grid(
    row=0,
    column=2,
    padx=5
)


# =========================================================
# SEARCH SECTION
# =========================================================

search_frame = tk.LabelFrame(
    root,
    text="Search Complaint",
    font=("Arial", 11, "bold"),
    padx=15,
    pady=10
)

search_frame.pack(
    pady=7
)

tk.Label(
    search_frame,
    text="Complaint ID:",
    font=("Arial", 10, "bold")
).pack(
    side="left",
    padx=5
)

search_entry = tk.Entry(
    search_frame,
    width=15
)

search_entry.pack(
    side="left",
    padx=5
)

search_button = tk.Button(
    search_frame,
    text="SEARCH",
    command=search_complaint,
    font=("Arial", 10, "bold"),
    padx=15,
    pady=5
)

search_button.pack(
    side="left",
    padx=5
)


# =========================================================
# STATUS UPDATE SECTION
# =========================================================

status_frame = tk.LabelFrame(
    root,
    text="Update Complaint Status",
    font=("Arial", 11, "bold"),
    padx=15,
    pady=10
)

status_frame.pack(
    pady=7
)

tk.Label(
    status_frame,
    text="Complaint ID:",
    font=("Arial", 10, "bold")
).pack(
    side="left",
    padx=5
)

status_id_entry = tk.Entry(
    status_frame,
    width=12
)

status_id_entry.pack(
    side="left",
    padx=5
)

status_combo = ttk.Combobox(
    status_frame,
    values=[
        "Pending",
        "In Progress",
        "Resolved"
    ],
    width=17,
    state="readonly"
)

status_combo.pack(
    side="left",
    padx=5
)

update_button = tk.Button(
    status_frame,
    text="UPDATE STATUS",
    command=update_status,
    font=("Arial", 10, "bold"),
    padx=15,
    pady=5
)

update_button.pack(
    side="left",
    padx=5
)


# =========================================================
# MAINTENANCE BUTTONS
# =========================================================

maintenance_frame = tk.Frame(
    root
)

maintenance_frame.pack(
    pady=7
)

maintenance_button = tk.Button(
    maintenance_frame,
    text="ADD MAINTENANCE DETAILS",
    command=open_maintenance_window,
    font=("Arial", 10, "bold"),
    padx=15,
    pady=7
)

maintenance_button.grid(
    row=0,
    column=0,
    padx=5
)

view_maintenance_button = tk.Button(
    maintenance_frame,
    text="VIEW MAINTENANCE",
    command=view_maintenance,
    font=("Arial", 10, "bold"),
    padx=15,
    pady=7
)

view_maintenance_button.grid(
    row=0,
    column=1,
    padx=5
)


# =========================================================
# REPORT & CHARTS
# =========================================================

analytics_frame = tk.LabelFrame(
    root,
    text="Reports & Analytics",
    font=("Arial", 11, "bold"),
    padx=15,
    pady=10
)

analytics_frame.pack(
    pady=8
)

report_button = tk.Button(
    analytics_frame,
    text="GENERATE REPORT",
    command=generate_report,
    font=("Arial", 10, "bold"),
    padx=15,
    pady=7
)

report_button.grid(
    row=0,
    column=0,
    padx=5
)

chart_button = tk.Button(
    analytics_frame,
    text="SHOW STATUS CHART",
    command=show_status_chart,
    font=("Arial", 10, "bold"),
    padx=15,
    pady=7
)

chart_button.grid(
    row=0,
    column=1,
    padx=5
)

category_chart_button = tk.Button(
    analytics_frame,
    text="SHOW CATEGORY CHART",
    command=show_category_chart,
    font=("Arial", 10, "bold"),
    padx=15,
    pady=7
)

category_chart_button.grid(
    row=0,
    column=2,
    padx=5
)


# =========================================================
# INITIAL DASHBOARD UPDATE
# =========================================================

refresh_dashboard()


# =========================================================
# START APPLICATION
# =========================================================

root.mainloop()