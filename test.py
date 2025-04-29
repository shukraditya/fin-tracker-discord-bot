from google import genai
import os

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
prompt_template = """
Extract the following information from the input sentence and return it as a JSON object in this format:
{{
  "amount": <amount spent as a number>,
  "place": <place where the money was spent>,
  "purpose": <purpose of the spending>,
  "spend_time": <date and time in ISO 8601 format for today>
}}
Input sentence:
{input_sentence}

Return only the JSON object.
"""

str="!add I spent 200 rupees at RAmeshwaram for lunch today"

if str.startswith('!add'):
    content = str.split('!add')[1].strip()
    prompt = prompt_template.format(input_sentence=content)
    
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=[prompt]
    )
    print(response.text)



