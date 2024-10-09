import re
def extract_code(text,language):
    # Use regex to extract the content inside triple backticks
    pattern = fr'```{language}(.*?)```'
    # Use regex to extract the content inside the dynamically created backticks
    code_blocks = re.findall(pattern, text, re.DOTALL)
    code_blocks = ''.join(code_blocks)
    return code_blocks

def extract_java_code(data):
    # Regular expression to extract Java code blocks from markdown-style code blocks (```)
    java_code_pattern = r'```(java)?\n(.*?)```'
    java_code_matches = re.findall(java_code_pattern, data, re.DOTALL)
    # mycode = ''.join(java_code_matches)
    mycode = ''.join(match[1] for match in java_code_matches)

    # Extracting and printing Java code from matches found in string data.
    # for match in java_code_matches:
    #     print(match.strip())

    return mycode