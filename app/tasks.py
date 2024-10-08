import psycopg2  # Or use pyodbc for SQL Server
import requests
import json
from sqlalchemy import create_engine, text
from app import utils
from .models import ProcedureConversion, DatabaseDetail, Audit
from app import db
import os
import re
from .git_actions import push_to_git
from .groq_api import get_model_reponse
from .utils import extract_code
import time

def get_stored_procedures(connection):
    # get_select_query(connection, query, initial=0)

    # # Update with your database connection details
    # conn = psycopg2.connect(
    #     dbname="sample", user="admin", password="password", host="localhost"
    # )
    # cursor = connection


    # Query to get stored procedures from PostgreSQL or SQL Server
    result = connection.execute(text("""
        SELECT routine_name, routine_definition
        FROM information_schema.routines
        WHERE routine_type = 'PROCEDURE';
    """))

    stored_procedures = result.fetchall()
    connection.close()
    # conn.close()
    print("Stored Procedures:", stored_procedures)
    return stored_procedures

def get_procedures_with_nested_calls(conn):
    # conn = engine.connect()
    # Step 1: Get the list of procedures and their definitions
    result = conn.execute(text(""" 
        SELECT routine_name, routine_definition 
        FROM information_schema.routines 
        WHERE routine_type = 'PROCEDURE'; 
    """))

    procedures = result.fetchall()
    procedure_dict = {routine_name: routine_definition for routine_name, routine_definition in procedures}

    # Step 2: Get the parameters for each procedure
    param_result = conn.execute(text(""" 
        SELECT 
            r.routine_name,
            p.parameter_name,
            p.data_type,
            p.parameter_mode 
        FROM 
            information_schema.routines r 
        JOIN 
            information_schema.parameters p 
        ON 
            r.specific_name = p.specific_name 
        WHERE 
            r.routine_type = 'PROCEDURE' 
        ORDER BY 
            r.routine_name, p.ordinal_position; 
    """))

    # Create a dictionary to hold parameter details
    param_dict = {}
    for row in param_result.fetchall():
        proc_name = row[0]
        param_name = row[1]
        param_type = row[2]
        param_mode = row[3]

        if proc_name not in param_dict:
            param_dict[proc_name] = []

        param_dict[proc_name].append({
            'name': param_name,
            'type': param_type,
            'mode': param_mode
        })

    # Step 3: Regular expression to find calls to other procedures
    call_pattern = re.compile(r'CALL\s+([a-zA-Z_][a-zA-Z0-9_]*)')

    # Step 4: Create a dictionary for the final output
    final_queries = {}

    # Step 5: Analyze each procedure's definition
    for routine_name, routine_definition in procedures:
        # Start building the query for the current procedure
        final_query = f"-- Procedure: {routine_name}\n"

        # Add parameters
        if routine_name in param_dict:
            params = param_dict[routine_name]
            input_params = [f"{param['name']}" for param in params if param['mode'] == 'IN']
            final_query += f"# Parameters: {', '.join(input_params)}\n"

        final_query += routine_definition + "\n\n"  # Add the actual procedure code

        # Find nested calls
        calls = call_pattern.findall(routine_definition)
        final_query +=""" Please use the below import function for nested method call for above procedures, dont use .  , dont create it.
         keep those in top of the code . 
        """
        for nested_call in calls:
            if nested_call in procedure_dict:
                # Prepare input parameters for the nested call
                nested_params = param_dict.get(nested_call, [])
                input_params = [f"{param['name']}" for param in nested_params if param['mode'] == 'IN']
                output_params = [f"{param['name']}" for param in nested_params if param['mode'] == 'OUT']

                # Format the method call as Python function
                final_query += f"{', '.join(output_params)} = {nested_call}({', '.join(input_params)})\n"

                # Add nested procedure definition
                # final_query += f"-- Nested Procedure: {nested_call}\n"
                # final_query += procedure_dict[nested_call] + "\n\n"

        # Store the complete query in the dictionary
        final_queries[routine_name] = final_query

    return final_queries




def convert_sql_to_python(sql_procedure):
    api_url = "http://localhost:11434/api/generate"
    model =  "codellama:7b"

    # Prepare the payload with the SQL procedure as the prompt
    payload = {
        "model": model,
        "prompt": f""" You are a code migrate code assistant, Convert the following SQL stored procedure into equivalent Python code using the sqlalchemy , database connections , pandas library (for data transformations and queries) and include a full database connection.  {sql_procedure}""",
        # "temperature": 0.1,
        "stream": False
    }

    # Send the request to Ollama API
    response = requests.post(api_url, data=json.dumps(payload), headers={"Content-Type": "application/json"})

    if response.status_code == 200:
        # Return the generated Python code
        resp_text = response.json()['response']
        if '```python' in resp_text:
            code_text = extract_code(resp_text,'python')
            # if len(code_text)>=1:
            #     code_text=code_text[0]
        else:
            code_text = extract_code(resp_text, '')
            # if len(code_text)>=1:
            #     code_text=code_text[0]
        print(code_text)
        return code_text
    else:
        raise Exception(f"API call failed: {response.status_code} - {response.text}")


def generate_testcase(code_text):
    api_url = "http://localhost:11434/api/generate"
    model = "codellama:7b"
    test_case_payload = {
        "model": model,
        "prompt": code_text,
        # "temperature": 0.1,
        "stream": False
    }
    testcase_response = requests.post(api_url, data=json.dumps(test_case_payload),
                                      headers={"Content-Type": "application/json"})
    test_resp_text = testcase_response.json()['response']
    if '```python' in test_resp_text:
        test_code_text = extract_code(test_resp_text, 'python')
        # if len(code_text)>=1:
        #     code_text=code_text[0]
    else:
        test_code_text = extract_code(test_resp_text, '')
    print(test_code_text)
    return test_code_text

python_code_file_folder = 'procedures'
os.makedirs(python_code_file_folder, exist_ok=True)

# 3. Store translated Python code
def store_translated_code(procedure_name, python_code):
    # Save the Python code into a file named after the procedure
    file_name = os.path.join(python_code_file_folder,f"{procedure_name}.py")
    with open(file_name, "w") as file:
        file.write(python_code)
    return file_name

def add_audit(msg,stage,db_id):
    audit_r = Audit(message= msg, stage=stage, database_id=db_id)
    db.session.add(audit_r)
    db.session.commit()


def update_status(msg,db_id):
    db_dt = db.session.query(DatabaseDetail).filter(DatabaseDetail.id == db_id).first()
    db_dt.status =msg # 'In Progress'
    db.session.commit()

def read_python_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def update_procedure_details(procedures,database_id):
    for proc in procedures:
        # Check if the record already exists
        procedure = db.session.query(ProcedureConversion).filter(ProcedureConversion.procedure_name == proc[0],ProcedureConversion.database_id == database_id,).first()
        if procedure:
            procedure.sql_code = proc[1]
            db.session.commit()
        else:
            procedures = ProcedureConversion(procedure_name = proc[0], sql_code = proc[1], database_id = database_id)
            db.session.add(procedures)
            db.session.commit()


def convert_procedures_task(items):
    # file_path='procedures/transfer.py'
    if isinstance(items,list):
        for item in items:
            process_migration(item)
    else:
        process_migration(items)

def process_migration(item):
    resp = 'Convertion Completed Successfully!'
    try:
        update_status('In Progress',item.id)
        connection1, engine1 = utils.db_conn1(item.id)
        # Get all stored procedures from the database
        # procedures = get_stored_procedures(connection1)
        # sp_with_nested_sp_calls = get_procedures_with_nested_calls()
        procedures = get_procedures_with_nested_calls(connection1)

        print('Read the procedures is done')
        update_procedure_details(procedures, item.id)
        add_audit('Done ', 'Procedures', item.id)
        if True:
            files_list=[]
            for procedure_name,procedure_sql in procedures.items():
                time.sleep(5)
                print(procedure_name)
                print(procedure_sql)
                print('------------------------')
                # procedure_name = proc[0]  # Procedure name
                # procedure_sql = proc[1]  # SQL definition

                # Convert SQL to Python using the API
                try:
                    # python_code = convert_sql_to_python(item.conversion_prompt.format(input=procedure_sql))
                    cv_prompt = item.conversion_prompt.format(input=procedure_sql)
                    python_code = get_model_reponse(cv_prompt)
                    print(f"Converted {procedure_name} into python successfully.")
                    add_audit(f"Converted SQL {procedure_name} successfully", 'SQL to Python Conversion', item.id)
                    # Store the translated Python code
                    filepath = store_translated_code(procedure_name, python_code)
                    files_list.append(filepath)
                    procedure = db.session.query(ProcedureConversion).filter(ProcedureConversion.database_id==item.id,ProcedureConversion.procedure_name==procedure_name).first()
                    procedure.python_file = filepath
                    procedure.python_code = python_code
                    db.session.commit()

                    print('Completed Code Migration')
                    prompt_txt = item.unittestcase_prompt
                    python_code = read_python_file(filepath)
                    prompt_txt = prompt_txt.format(input=python_code)
                    testcase_code = get_model_reponse(prompt_txt)
                    testcase_file = store_translated_code('UnitTest'+procedure_name, testcase_code)
                    add_audit(f"Generated Test case for  {procedure_name} successfully", 'Test Case Generation', item.id)

                    files_list.append(testcase_file)
                    procedure = db.session.query(ProcedureConversion).filter(ProcedureConversion.database_id==item.id,ProcedureConversion.procedure_name==procedure_name).first()
                    procedure.testcase_file = testcase_file
                    procedure.testcase_code = testcase_code
                    db.session.commit()
                except Exception as e:
                    resp='Failed to process! Please check the log!'
                    print(f"Failed to convert {procedure_name}: {e}")  #
                    update_status('Failed',item.id)
                    add_audit(f"Failed to convert {procedure_name}: {e}", 'Migration', item.id)

            # files_list = ['procedures/transfer.py', 'procedures/UnitTesttransfer.py']

            print('processing git')
            msg = push_to_git(item.id, files_list)
            print('done git')
            update_status(msg,item.id)
    except Exception as e:
        raise e
        resp = 'Failed to process! Please check the log!'
        update_status('Failed', item.id)
        add_audit(f"Failed to Process : {e}", 'Migration Process', item.id)
    return resp