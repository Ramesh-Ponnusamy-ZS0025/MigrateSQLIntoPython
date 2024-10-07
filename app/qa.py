#pip install python-docx

from docx import Document
from .groq_api import get_llm_response
from .common import extract_code
from config import UPLOAD_FOLDER
import os

def read_docx(file_path):
    # Load the DOCX file
    doc = Document(os.path.join(UPLOAD_FOLDER,file_path))
    # Initialize an empty string to store the content
    full_text = []
    # Iterate through each paragraph in the document
    for para in doc.paragraphs:
        full_text.append(para.text)  # Append the paragraph text to the list
    # Join the list into a single string with newline characters
    return '\n'.join(full_text)

def write_string_to_file(file_path, content):
    # Open the file in write mode (this will overwrite the file if it exists)
    with open(os.path.join(UPLOAD_FOLDER,file_path), 'w', encoding='utf-8') as file:
        file.write(content)

def process_qa_llm(file_path,file_id):
    prompt = read_docx(file_path)
    prompt += """" 
            Output Requirements:
            From the user story, please generate the following documents:
            
            Acceptance Criteria Document:
            Create a document outlining the acceptance criteria for the delete connection feature.
            add line "process_zuci_is_done"
            
            BDD-Style Test Cases Document:
            Generate a document containing BDD-style test cases derived from the acceptance criteria.
            add line "process_zuci_is_done"
            
            Selenium Cucumber Java Test Automation Script:
            Develop a complete Selenium Cucumber java  test automation complete script that includes:
            A feature file reflecting the BDD test cases.
            A step definition file that implements the necessary automation steps.  
            add line "process_zuci_is_done" 
           """
    # content +=prompt
    content_response = get_llm_response(prompt)
    print(content_response)
    split_response = content_response.split('process_zuci_is_done')
    print(len(split_response))
    print(split_response)
    acceptance_criteria_content = split_response[0]
    bdd_style_test_case_content = split_response[1]
    java_code = extract_code(split_response[2], 'java')
    base_filename = os.path.splitext(os.path.basename(file_path))[0]
    base_filename +="_"+str(file_id)
    ac_file_path = base_filename + '_acceptance_criteria.docx'
    bdd_file_path = base_filename + '_bdd_style_test_case.docx'
    java_file_path = base_filename + '_test_script.java'
    write_string_to_file(ac_file_path,acceptance_criteria_content)
    write_string_to_file(bdd_file_path, bdd_style_test_case_content)
    write_string_to_file(java_file_path, java_code)
    return ac_file_path,bdd_file_path,java_file_path





