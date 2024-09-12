import psycopg2  # Or use pyodbc for SQL Server
import requests
import json
from sqlalchemy import create_engine, text
from app import utils
from .models import ProcedureConversion, DatabaseDetail, Audit
from app import db
import os

from .git_actions import push_to_git

def get_stored_procedures(connection):
    # get_select_query(connection, query, initial=0)

    # # Update with your database connection details
    # conn = psycopg2.connect(
    #     dbname="sample", user="admin", password="password", host="localhost"
    # )
    # cursor = connection

    print('conection',connection)
    # Query to get stored procedures from PostgreSQL or SQL Server
    result = connection.execute(text("""
        SELECT routine_name, routine_definition
        FROM information_schema.routines
        WHERE routine_type = 'PROCEDURE';
    """))

    stored_procedures = result.fetchall()
    connection.close()
    # conn.close()

    return stored_procedures


def convert_sql_to_python(sql_procedure):
    api_url = "http://localhost:11434/api/generate"
    model = "codellama:7b"

    # Prepare the payload with the SQL procedure as the prompt
    payload = {
        "model": model,
        "prompt": f"""C1.first Convert the following SQL stored procedure into equivalent Python code using the 
sqlalchemy with raw sql query, database connections , pandas library (for data transformations and queries) and include a full database connection. 
Note: Provide only the code ,no explanations or comments.: {sql_procedure}""",
        "stream": False
    }

    # Send the request to Ollama API
    response = requests.post(api_url, data=json.dumps(payload), headers={"Content-Type": "application/json"})

    if response.status_code == 200:
        # Return the generated Python code
        resp_text = response.json()['response']
        if '```python' in resp_text:
            code_text = ''.join(resp_text.split('```python')[1::][0])
        else:
            code_text = ''.join(resp_text.split('```')[1::][0])
        return code_text
    else:
        raise Exception(f"API call failed: {response.status_code} - {response.text}")


def generate_testcase(code_text):
    api_url = "http://localhost:11434/api/generate"
    model = "codellama:python"
    test_case_payload = {
        "model": model,
        "prompt": f""" write a unit test for this function:  {code_text}  Note: Provide only the code , no explanations or comments.  """,
        "stream": False
    }
    print(test_case_payload)
    testcase_response = requests.post(api_url, data=json.dumps(test_case_payload),
                                      headers={"Content-Type": "application/json"})
    test_resp_text = testcase_response.json()['response']
    print(testcase_response.json())
    if '```python' in test_resp_text:
        test_code_text = ''.join(test_resp_text.split('```python')[1::])
    else:
        test_code_text = ''.join(test_resp_text.split('```')[1::])
    return test_code_text

python_code_file_folder = 'procedures'
os.makedirs(python_code_file_folder, exist_ok=True)

# 3. Store translated Python code
def store_translated_code(procedure_name, python_code):
    # Save the Python code into a file named after the procedure
    file_name = os.path.join(python_code_file_folder,f"{procedure_name}.py")
    with open(file_name, "w") as file:
        file.write(python_code)
    print('file_name',file_name)
    return file_name

def add_audit(msg,stage,db_id):
    audit_r = Audit(message= msg, stage=stage, database_id=db_id)
    db.session.add(audit_r)
    db.session.commit()


def update_status(msg,db_id):
    db_dt = db.session.query(DatabaseDetail).filter(DatabaseDetail.id == db_id).first()
    db_dt.status =msg # 'In Progress'
    db.session.commit()

def convert_procedures_task(items):
    for item in items:
        try:
            update_status('In Progress',item.id)
            connection1, engine1 = utils.db_conn1(item.id)
            # Get all stored procedures from the database
            procedures = get_stored_procedures(connection1)
            print('procedures')
            add_audit('Done ', 'Procedures', item.id)
            if True:
                files_list=[]
                for proc in procedures:
                    procedure_name = proc[0]  # Procedure name
                    procedure_sql = proc[1]  # SQL definition

                    # Convert SQL to Python using the API
                    try:
                        python_code = convert_sql_to_python(procedure_sql)
                        print(f"Converted {procedure_name} successfully.")
                        add_audit(f"Converted SQL {procedure_name} successfully", 'SQL to Python Conversion', item.id)
                        # Store the translated Python code
                        filepath = store_translated_code(procedure_name, python_code)
                        files_list.append(filepath)
                        procedures = ProcedureConversion(procedure_name='test_user',python_file=filepath,
                                                        testcase_file='',python_code=python_code,
                                                        testcase_code='',
                                                        database_id=item.id)
                        db.session.add(procedures)
                        db.session.commit()
                        proceduresid = procedures.id
                        print('Completed Code')
                        testcase_code = generate_testcase(python_code)
                        testcase_file = store_translated_code('UnitTest'+procedure_name, testcase_code)
                        add_audit(f"Generated Test case for  {procedure_name} successfully", 'Test Case Generation', item.id)

                        files_list.append(testcase_file)
                        procedure = db.session.query(ProcedureConversion).filter(ProcedureConversion.id == proceduresid).first()
                        procedure.testcase_file = testcase_file
                        procedure.testcase_code = testcase_code
                        db.session.commit()
                        print('Saved',testcase_file)

                    except Exception as e:
                        print(f"Failed to convert {procedure_name}: {e}")  #
                        update_status('Failed',item.id)
                        add_audit(f"Failed to convert {procedure_name}: {e}", 'Migration', item.id)

                # files_list = ['procedures/transfer.py', 'procedures/UnitTesttransfer.py']

                print('processing git')
                msg = push_to_git(item.id, files_list)
                print('done git')
                update_status(msg,item.id)
        except Exception as e:
            update_status('Failed', item.id)
            add_audit(f"Failed to Process : {e}", 'Migration Process', item.id)