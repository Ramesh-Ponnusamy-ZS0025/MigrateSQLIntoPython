import re
def extract_code(text,language):
    # Use regex to extract the content inside triple backticks
    pattern = fr'```{language}(.*?)```'
    # Use regex to extract the content inside the dynamically created backticks
    code_blocks = re.findall(pattern, text, re.DOTALL)
    code_blocks = ''.join(code_blocks)
    return code_blocks