
from groq import Groq
from .utils import extract_code
api_key = "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"



client = Groq(
    api_key=api_key,
)

def get_model_reponse(prompt):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="llama3-8b-8192",
    )
    response = chat_completion.choices[0].message.content
    if '```python' in response:
        code_text = extract_code(response, 'python')
        # if len(code_text)>=1:
        #     code_text=code_text[0]
    else:
        code_text = extract_code(response, '')
    return code_text

