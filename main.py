import os
import io
import re
import discord
from dotenv import load_dotenv
from PIL import Image
from scoreboard_to_data import ValorantScoreboardParser
from google import genai

# Load your bot token from .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
ALLOWED_NAMES = {'snippy' : '@snippy4', 
'masochist' : '@alsilvs', 
'sweetcorn' : '@zetabomb', 
'switch' : '@t0mmy77', 
'betajumper' : '@betajumper', 
'gutz'  : '@angiegutz',
'sadist' : '@mucchan9295', 
'glitch' : '@glitch6164',
 'ginger' : '@liviajt', 
 'papi' : '@dchester', 
 'aiyeo' : '@aiyeo', 
 'aeo' : '@aiyeo'}
genaiclient = genai.Client()

# Replace with the channel ID you want to read messages from
TARGET_CHANNEL_ID = 1424379611692924998  # 👈 your channel ID as an integer

# Enable message content intent (required to read messages)
intents = discord.Intents.default()
intents.message_content = True

def generate_roast(scoreboarded_pairs):
    pairs_text = []
    for p1, p2 in scoreboarded_pairs:
        pairs_text.append(f"<{ALLOWED_NAMES[p2['name'].lower()]}> ({p2['score']} score, {p2['kills']} kills) got scoreboarded in valorant by <{ALLOWED_NAMES[p1['name'].lower()]}> ({p1['score']} score, {p1['kills']} kills)")
    prompt = f"Write a quick, funny roast that isnt too long and isnt too short for {pairs_text}\
     this is a friendly inside joke so be as savage as you want, make your message informal, dont use too much punctuation, and use language you would expect a chronically online 18 year old to use.\
     feel free to use profanity, curse words, and insulting words that may be offensive as well as realistic text speak\
     this prompt is for a bot to send a discord message so only write one message for the roast and include any players that got scoreboarded."
    response = genaiclient.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    return response.text

# Create a client instance
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    print("Listening for messages in channel:", TARGET_CHANNEL_ID)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.channel.id != TARGET_CHANNEL_ID:
        return

    if message.attachments:
        for attachment in message.attachments:
            if not attachment.content_type and not attachment.content_type.startswith("image/"):
                return
            print(f"Processing image from {message.author}: {attachment.filename}")

            # Download image
            image_bytes = await attachment.read()
            image = Image.open(io.BytesIO(image_bytes))
            image.save('image.png')
            scorebaording = ValorantScoreboardParser('image.png')
            scoreboarded = scorebaording.find_scoreboarding()
            scoreboarded = [(p1, p2) for p1, p2 in scoreboarded 
            if p1['name'].lower() in ALLOWED_NAMES and p2['name'].lower() in ALLOWED_NAMES]
            print(scoreboarded)


            if scoreboarded:
                p1 = scoreboarded[0][0]
                p2 = scoreboarded[0][1]
                roast = generate_roast(scoreboarded)
                await message.channel.send(f"{roast}")
                await message.add_reaction("<:snippy:1425117427301089400>")
               
client.run(TOKEN)
