import streamlit as st
import sqlite3
import pandas as pd
import google.generativeai as genai
import os
from dotenv import load_dotenv

# --- 1. LOAD ENVIRONMENT VARIABLES ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("API Key not found. Please check your .env file.")

# --- 2. CORE FUNCTIONS ---

def get_gemini_sql(question, prompt_list):
    """Generates SQL query from natural language using Gemini."""
    try:
        # Note: 'gemini-2.0-flash' or 'gemini-1.5-flash' are current versions. 
        # Ensure the model name matches the latest available versions.
        model = genai.GenerativeModel('gemini-2.5-flash') 
        response = model.generate_content([prompt_list[0], question])
        
        # Clean the output to ensure it is pure SQL
        sql_query = response.text.strip()
        sql_query = sql_query.replace("```sql", "").replace("```", "").replace(";", "")
        return sql_query
    except Exception as e:
        return f"Error generating SQL: {str(e)}"

def explain_sql_query(query):
    """Explains the generated SQL query in plain English."""
    try:
        explain_prompt = f"Explain this SQL query step-by-step in simple terms:\n{query}"
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(explain_prompt)
        return response.text.strip()
    except Exception as e:
        return f"Could not generate explanation: {str(e)}"

def read_sql_query(sql, db):
    """Executes the SQL query on the local SQLite database."""
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        col_names = [desc[0] for desc in cur.description]
        conn.close()
        return rows, col_names
    except sqlite3.Error as e:
        return [("SQL Error", str(e))], ["Error"]

# --- 3. PROMPT CONFIGURATION ---

prompt = ["""
# Context:
You are an expert SQL assistant translating English to SQLite for the 'Naresh_it_employee1' table.

# Schema:
- Table: Naresh_it_employee1
- Columns: employee_name (text), employee_role (text), employee_salary (float)

# Constraints:
- Use only SQLite syntax.
- Do NOT use backticks (`), triple quotes (```), or semicolons.
- Return ONLY the SQL query string.

# Examples:
Q: Who earns the highest salary?
A: SELECT * FROM Naresh_it_employee1 ORDER BY employee_salary DESC LIMIT 1

Q: Average salary of Data Engineers?
A: SELECT AVG(employee_salary) FROM Naresh_it_employee1 WHERE employee_role = 'Data Engineer'

Now generate the SQL query for:
"""]

# --- 4. STREAMLIT UI ---

st.set_page_config(page_title="LLM SQL Assistant", layout="wide")
st.title("🚀 Gemini SQL App")
st.write("Interact with your Employee Database using Natural Language.")

# Sidebar for help/status
with st.sidebar:
    st.success("API Key Loaded" if api_key else "API Key Missing")
    st.info("Database: Naresh_it_employee1.db")

# User input
question = st.text_input("Enter your question:", placeholder="e.g., Show me the top 3 highest paid employees")

if st.button("Generate & Run"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        # Step 1: Generate SQL
        sql_query = get_gemini_sql(question, prompt)
        
        if "Error" in sql_query:
            st.error(sql_query)
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Generated SQL")
                st.code(sql_query, language="sql")
                
                # Step 2: Run Query
                result, columns = read_sql_query(sql_query, "Naresh_it_employee1.db")
                
                st.subheader("Query Result")
                if result and "SQL Error" in result[0]:
                    st.error(f"Execution Error: {result[0][1]}")
                else:
                    df = pd.DataFrame(result, columns=columns)
                    st.dataframe(df, use_container_width=True)

            with col2:
                # Step 3: Explain Query
                st.subheader("Query Explanation")
                explanation = explain_sql_query(sql_query)
                st.info(explanation)