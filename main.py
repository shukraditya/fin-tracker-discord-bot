import discord
from dotenv import load_dotenv
import os
from google import genai
from datetime import datetime
from pydantic import BaseModel
import gspread
from google.oauth2.service_account import Credentials
import requests


SERVICE_ACCOUNT_FILE = 'fin-track-discord-bot-1836ac2f6820.json' #path to service file
url = 'https://docs.google.com/spreadsheets/d/1hwVs4yW7bIbCzUPzstPpFGKqr2QWXW56Dfph66bGJfA/edit?gid=0#gid=0'



scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
gsheet_client = gspread.authorize(creds)

sheet = gsheet_client.open_by_url(url).sheet1  # or .worksheet('Sheet1')


load_dotenv() #env vars loaded
gem_client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

class Expense(BaseModel):
    amount: int
    place: str
    purpose: str
    spend_date: str



intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)





@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    ## adding via text natural language
    if message.content.startswith('!add '):
        current_date = datetime.now().strftime("%Y-%m-%d")
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
        content = message.content.split('!add')[1].strip()
        prompt = prompt_template.format(input_sentence=content,current_date=current_date)
        response = gem_client.models.generate_content(
            model="gemini-2.0-flash", contents=[prompt],
            config={
                'response_mime_type':'application/json',
                'response_schema':Expense,
            },
        )
        amount = response.parsed.amount
        place = response.parsed.place
        purpose = response.parsed.purpose
        spend_date = response.parsed.spend_date
        row = [amount, place, purpose, spend_date]
        sheet.append_row(row)
        await message.channel.send(f'Added to sheet \nAmount: {amount} \nPlace: {place} \nPurpose: {purpose} \nSpend Date:{spend_date}')
    
    
    
    
    #   feature coming soon
    ## adding via bill feature coming soon
    if message.attachments and message.content.startswith('!add-p'):
        for attachment in message.attachments:
            if attachment.content_type and attachment.content_type.startswith('image/'):
                # Get the image URL
                image_url = attachment.url
                img_path = "local_image.jpg"

                with requests.get(image_url, stream=True) as r:
                    r.raise_for_status()
                    with open(img_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                
                with open(img_path, "rb") as f:
                    img_bytes = f.read()
                
                prompt = """
Extract the following information from this bill. If any field is missing, return null for that field.
Return only a JSON object in this format:
{
  "amount": <amount spent as a number>,
  "place": <place where the money was spent>,
  "purpose": <purpose of the spending>,
  "spend_time": <date in YYYY-MM-DD format>
}
Here is the bill image:
"""

                response = gem_client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[
                        genai.types.Part.from_bytes(data=img_bytes, mime_type='image/jpeg'),
                        prompt
                    ],
                    config={
                    'response_mime_type':'application/json',
                    'response_schema':Expense,
                    },
                )
                amount = response.parsed.amount
                place = response.parsed.place
                purpose = response.parsed.purpose
                spend_date = response.parsed.spend_date
                row = [amount, place, purpose, spend_date]
                sheet.append_row(row)
                await message.channel.send(f'Added to sheet \nAmount: {amount} \nPlace: {place} \nPurpose: {purpose} \nSpend Date:{spend_date}')
            





        
    
    # if message.attachments:
    #     for attachment in message.attachments:
    #         if attachment.content_type and attachment.content_type.startswith('image/'):
    #             # Get the image URL
    #             image_url = attachment.url
    #             await message.channel.send(f'Image Received! URL is: {image_url}')

                

client.run(os.getenv('DISCORD_BOT_TOKEN'))
