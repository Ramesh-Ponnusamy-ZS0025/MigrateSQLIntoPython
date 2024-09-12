import psycopg2  # Or use pyodbc for SQL Server
import requests
import json

def get_stored_procedures():
    # Update with your database connection details
    conn = psycopg2.connect(
        dbname="sample", user="admin", password="password", host="localhost"
    )
    cursor = conn.cursor()

    # Query to get stored procedures from PostgreSQL or SQL Server
    cursor.execute("""
        SELECT routine_name, routine_definition
        FROM information_schema.routines
        WHERE routine_type = 'PROCEDURE';
    """)

    stored_procedures = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return stored_procedures
    
def convert_sql_to_python(sql_procedure):
    api_url = "http://localhost:11434/api/generate"
    model = "codellama:7b"
    
    # Prepare the payload with the SQL procedure as the prompt
    payload = {
        "model": model,
        "prompt": f"""C1.first Convert the following SQL stored procedure into equivalent Python code using the 
sqlalchemy, database connections , pandas library (for data transformations and queries) and include a full database connection. 
Note: Provide only the code ,no explanations or comments.: {sql_procedure}""",
        "stream": False
    }
    
    # Send the request to Ollama API
    response = requests.post(api_url, data=json.dumps(payload), headers={"Content-Type": "application/json"})
    
    if response.status_code == 200:
        # Return the generated Python code
        resp_text = response.json()['response']
        code_text = ''.join(resp_text.split('```')[1::][0])
        return code_text
    else:
        raise Exception(f"API call failed: {response.status_code} - {response.text}")

# 3. Store translated Python code
def store_translated_code(procedure_name, python_code):
    # Save the Python code into a file named after the procedure
    file_name = f"{procedure_name}.py"
    with open(file_name, "w") as file:
        file.write(python_code)

# Get all stored procedures from the database
procedures = get_stored_procedures()

if True:
    for proc in procedures:
        procedure_name = proc[0]  # Procedure name
        procedure_sql = proc[1]   # SQL definition

        # Convert SQL to Python using the API
        try:
            python_code = convert_sql_to_python(procedure_sql)
            print(f"Converted {procedure_name} successfully.")
            
            # Store the translated Python code
            store_translated_code(procedure_name, python_code)
        except Exception as e:
            print(f"Failed to convert {procedure_name}: {e}")#       
