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
ALLOWED_NAMES = {'snippy' : '345254471753924611', 
'masochist' : '294868726313123870', 
'sweetcorn' : '370258922868572172', 
'switch' : '610223436522061853', 
'betajumper' : '364856743441989633', 
'gutz'  : '362310474798202881',
'sadist' : '452533933452689439', 
'glitch' : '754721639010140272',
 'ginger' : '406485851699281936', 
 'papi' : '77074956743086080', 
 'aiyeo' : '342433750409281536', }
genaiclient = genai.Client()

# Replace with the channel ID you want to read messages from
MOMENTS_CHANNEL_ID = 1065429100199686234  # 👈 your channel ID as an integer
TEST_CHANNEL_ID = 1424379611692924998  # 👈 your channel ID as an integer
SPAM_CHANNEL_ID = 1194066107821195355
# Enable message content intent (required to read messages)
intents = discord.Intents.default()
intents.message_content = True

def generate_valorant_roast(scoreboarded_pairs):
    pairs_text = []
    for p1, p2 in scoreboarded_pairs:
        pairs_text.append(f"<@{ALLOWED_NAMES[p2['name'].lower()]}> ({p2['score']} score, {p2['kills']} kills) got scoreboarded in valorant by <@{ALLOWED_NAMES[p1['name'].lower()]}> ({p1['score']} score, {p1['kills']} kills)")
    prompt = f"Write a quick, funny roast that isnt too long and isnt too short for {pairs_text}\
     this is a friendly inside joke so be as savage as you want, make your message informal, dont use too much punctuation, and use language you would expect a chronically online 18 year old to use.\
     feel free to use profanity, curse words, and insulting words that may be offensive as well as realistic text speak\
     this prompt is for a bot to send a discord message so only write one message for the roast and include any players that got scoreboarded."
    response = genaiclient.models.generate_content(model="gemma-3-1b", contents=prompt)
    return response.text

def generate_wordle_roast(people):
    prompt = f"{people.split(' ')} failed the wordle yesterday, yikes. write a quick funny roast about how they failed the wordle.\
    This is part of a friendly inside joke so feel free to be as mean as you like, you can use profanity and personal insults. you should also talk like a chronically online 18 year old using realistic text speak.\
    this prompt is for a discord bot message reply so only reply with one message for the roast."
    response = genaiclient.models.generate_content(model="gemma-3-1b", contents=prompt)
    return response.text

async def check_scoreboard(message):
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
                roast = generate_valorant_roast(scoreboarded)
                await message.channel.send(f"{roast}")
                await message.add_reaction("<:snippy:1208470366909890662>")

async def check_wordle_fail(message):
    msg = message.content
    if "X/6:" in msg:
        await message.channel.send(generate_wordle_roast(msg.split("X/6:")[1]))


# Create a client instance
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.channel.id == TEST_CHANNEL_ID:
        await message.channel.send("scoreboard bot is running smoothly")
        await check_scoreboard(message)
        await check_wordle_fail(message)
    if message.channel.id == MOMENTS_CHANNEL_ID:
        await check_scoreboard(message)
    if message.channel.id == SPAM_CHANNEL_ID:
        if message.author.id == 1211781489931452447:
            await check_wordle_fail(message)
    return
    

        

               
client.run(TOKEN)
