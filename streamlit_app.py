import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

DB = "campus_maintenance.db"

st.set_page_config(
    page_title="CampusFix",
    page_icon="🏫",
    layout="wide"
)

def get_connection():
    return sqlite3.connect(DB)

def get_complaints():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM complaints", conn)
    conn.close()
    return df

# ---------- HEADER ----------
st.title("🏫 CampusFix")
st.subheader("Campus Maintenance Complaint & Tracking System")
st.write("Report, track and manage campus maintenance complaints.")

# ---------- DASHBOARD ----------
df = get_complaints()

total = len(df)
pending = len(df[df["status"] == "Pending"]) if not df.empty else 0
progress = len(df[df["status"] == "In Progress"]) if not df.empty else 0
resolved = len(df[df["status"] == "Resolved"]) if not df.empty else 0

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Complaints", total)
c2.metric("Pending", pending)
c3.metric("In Progress", progress)
c4.metric("Resolved", resolved)

st.divider()

# ---------- SIDEBAR ----------
menu = st.sidebar.radio(
    "Menu",
    [
        "Register Complaint",
        "View Complaints",
        "Search Complaint",
        "Update Status",
        "Maintenance Details",
        "Reports"
    ]
)

# ---------- REGISTER ----------
if menu == "Register Complaint":

    st.header("Register New Complaint")

    with st.form("complaint_form"):

        col1, col2 = st.columns(2)

        with col1:
            student_name = st.text_input("Student Name")
            department = st.text_input("Department")
            building = st.text_input("Building")
            room_no = st.text_input("Room Number")

        with col2:
            category = st.selectbox(
                "Category",
                ["Electrical", "Plumbing", "Furniture", "Cleanliness", "Internet", "Other"]
            )

            priority = st.selectbox(
                "Priority",
                ["Low", "Medium", "High"]
            )

            description = st.text_area("Complaint Description")

        submitted = st.form_submit_button("Submit Complaint")

        if submitted:

            if not all([
                student_name,
                department,
                building,
                room_no,
                description
            ]):
                st.warning("Please fill all required fields.")

            else:

                conn = get_connection()
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO complaints
                    (student_name, department, building, room_no,
                     category, priority, description,
                     date_reported, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    student_name,
                    department,
                    building,
                    room_no,
                    category,
                    priority,
                    description,
                    datetime.now().strftime("%Y-%m-%d"),
                    "Pending"
                ))

                conn.commit()
                complaint_id = cursor.lastrowid
                conn.close()

                st.success(
                    f"Complaint registered successfully! Complaint ID: {complaint_id}"
                )

# ---------- VIEW ----------
elif menu == "View Complaints":

    st.header("All Complaints")

    if df.empty:
        st.info("No complaints found.")
    else:
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

# ---------- SEARCH ----------
elif menu == "Search Complaint":

    st.header("Search Complaint")

    complaint_id = st.number_input(
        "Enter Complaint ID",
        min_value=1,
        step=1
    )

    if st.button("Search"):

        conn = get_connection()

        result = pd.read_sql_query(
            "SELECT * FROM complaints WHERE complaint_id = ?",
            conn,
            params=(complaint_id,)
        )

        conn.close()

        if result.empty:
            st.error("Complaint not found.")
        else:
            st.success("Complaint found!")
            st.dataframe(
                result,
                use_container_width=True,
                hide_index=True
            )

# ---------- UPDATE STATUS ----------
elif menu == "Update Status":

    st.header("Update Complaint Status")

    complaint_id = st.number_input(
        "Complaint ID",
        min_value=1,
        step=1
    )

    new_status = st.selectbox(
        "New Status",
        ["Pending", "In Progress", "Resolved"]
    )

    if st.button("Update Status"):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE complaints SET status = ? WHERE complaint_id = ?",
            (new_status, complaint_id)
        )

        conn.commit()

        if cursor.rowcount == 0:
            st.error("Complaint ID not found.")
        else:
            st.success("Complaint status updated successfully!")

        conn.close()

# ---------- MAINTENANCE ----------
elif menu == "Maintenance Details":

    st.header("Maintenance Details")

    tab1, tab2 = st.tabs(
        ["Add Maintenance", "View Maintenance"]
    )

    with tab1:

        complaint_id = st.number_input(
            "Complaint ID",
            min_value=1,
            step=1
        )

        staff_name = st.text_input("Staff Name")
        work_done = st.text_area("Work Done")
        cost = st.number_input(
            "Cost",
            min_value=0.0,
            step=50.0
        )

        if st.button("Save Maintenance Details"):

            if not staff_name or not work_done:
                st.warning("Please fill all required fields.")

            else:

                conn = get_connection()
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO maintenance_details
                    (complaint_id, staff_name, work_done,
                     cost, maintenance_date)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    complaint_id,
                    staff_name,
                    work_done,
                    cost,
                    datetime.now().strftime("%Y-%m-%d")
                ))

                conn.commit()
                conn.close()

                st.success("Maintenance details saved successfully!")

    with tab2:

        conn = get_connection()

        maintenance = pd.read_sql_query(
            "SELECT * FROM maintenance_details",
            conn
        )

        conn.close()

        if maintenance.empty:
            st.info("No maintenance records found.")
        else:
            st.dataframe(
                maintenance,
                use_container_width=True,
                hide_index=True
            )

# ---------- REPORTS ----------
elif menu == "Reports":

    st.header("Reports & Analytics")

    if df.empty:
        st.info("No complaint data available.")
    else:

        st.subheader("Status Report")

        status_report = df["status"].value_counts()

        st.bar_chart(status_report)

        st.subheader("Category Report")

        category_report = df["category"].value_counts()

        st.bar_chart(category_report)

        st.subheader("Priority Report")

        priority_report = df["priority"].value_counts()

        st.bar_chart(priority_report)

        st.subheader("Complaint Summary")

        st.write(f"Total complaints: **{total}**")
        st.write(f"Pending complaints: **{pending}**")
        st.write(f"In Progress complaints: **{progress}**")
        st.write(f"Resolved complaints: **{resolved}**")