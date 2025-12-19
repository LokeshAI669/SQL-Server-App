import streamlit as st
import sqlite3

# Set page config (optional)
st.set_page_config(page_title="Employee DB Viewer", layout="centered")

st.title("🧑‍💼 Naresh IT Employee Database")

# Connect to SQLite databSase
connection = sqlite3.connect("Naresh_it_employee1.db")
cursor = connection.cursor()

# Create table if not exists
table_info = """
CREATE TABLE IF NOT EXISTS Naresh_it_employee1 (
    employee_name VARCHAR(30),
    employee_role VARCHAR(30),
    employee_salary FLOAT
);  
"""
cursor.execute(table_info)

# Insert records only if table is empty
cursor.execute("SELECT COUNT(*) FROM Naresh_it_employee1")
count = cursor.fetchone()[0]

if count == 0:
    cursor.execute('''INSERT INTO Naresh_it_employee1 VALUES ('Omkar Nallagoni', 'Data Science', 75000)''')
    cursor.execute('''INSERT INTO Naresh_it_employee1 VALUES ('Naresh', 'Data Science', 90000)''')
    cursor.execute('''INSERT INTO Naresh_it_employee1 VALUES ('Phani', 'Data Science', 88000)''')
    cursor.execute('''INSERT INTO Naresh_it_employee1 VALUES ('Naga babu', 'Data Engineer', 50000)''')
    cursor.execute('''INSERT INTO Naresh_it_employee1 VALUES ('Ajay', 'Data Engineer', 35000)''')
    cursor.execute('''INSERT INTO Naresh_it_employee1 VALUES ('Pawan', 'Data Engineer', 60000)''')
    connection.commit()

# Display records
st.subheader("📋 Employee Records")
data = cursor.execute("SELECT * FROM Naresh_it_employee1")
rows = data.fetchall()

if rows:
    for row in rows:
        st.write(f"👤 **Name**: {row[0]} | 🧠 **Role**: {row[1]} | 💰 **Salary**: ₹{row[2]:,.2f}")
else:
    st.warning("No records found.")

# Close connection
connection.close()