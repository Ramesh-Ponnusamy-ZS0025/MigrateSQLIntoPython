
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
        model="llama3-70b-8192",
    )
    response = chat_completion.choices[0].message.content
    if '```python' in response:
        code_text = extract_code(response, 'python')
        # if len(code_text)>=1:
        #     code_text=code_text[0]
    else:
        code_text = extract_code(response, '')
    return code_text

