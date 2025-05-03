from google import genai
import os
from datetime import datetime
import json
from pydantic import BaseModel


class Expense(BaseModel):
    amount: int
    place: str
    purpose: str
    spend_time: datetime








current_date = datetime.now().strftime("%Y-%m-%d")
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
prompt_template = """
Extract the following information from the input sentence and return it as a JSON object in this format:
{{
  "amount": <amount spent as a number>,
  "place": <place where the money was spent>,
  "purpose": <purpose of the spending>,
  "spend_time": <date in YYYY-MM-DD format>
}}

Instructions:
- Extract the amount as a number.
- Extract the place name as it appears in the sentence.
- Extract the purpose of spending.
- For "spend_time", convert time references like "today", "yesterday", "two days ago", "last Monday", etc. to an actual date in YYYY-MM-DD format based on the current date of {current_date}.

Input sentence:
{input_sentence}

Return only the JSON object.
"""






str="!add i had lunch at rameshwaram cafe with my friend. bill was 200 rupees"




if str.startswith('!add'):
    content = str.split('!add')[1].strip()
    prompt = prompt_template.format(input_sentence=content,current_date=current_date)
    
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=[prompt],
        config={
            'response_mime_type':'application/json',
            'response_schema':Expense,
        },
    )

    res = response.parsed
    print(res.spend_time)
    



