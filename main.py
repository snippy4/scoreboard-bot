import os
import sys
import io
import re
import asyncio
from datetime import date
import discord
from dotenv import load_dotenv
from PIL import Image
from scoreboard_to_data import ValorantScoreboardParser
from google import genai

SELF_TEST = "--self-test" in sys.argv

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
 'aiyeo' : '342433750409281536',
 'twink destroyer' : '620302045773037569', }
genaiclient = genai.Client()
DAILY_IMAGE_LIMIT = 150
images_processed = 0
images_processed_date = date.today()

SCOREBOARD_CHANNELS = {1065429100199686234, 688450642498551815, 1424379611692924998}  # moments
WORDLE_CHANNELS = {1194066107821195355}  # spam
TEST_CHANNELS = {1424379611692924998}
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
    response = genaiclient.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    return response.text

def generate_wordle_roast(people):
    prompt = f"{people.split(' ')} failed the wordle yesterday, yikes. write a quick funny roast about how they failed the wordle.\
    This is part of a friendly inside joke so feel free to be as mean as you like, you can use profanity and personal insults. you should also talk like a chronically online 18 year old using realistic text speak.\
    this prompt is for a discord bot message reply so only reply with one message for the roast."
    response = genaiclient.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    return response.text

async def check_scoreboard(message):
    global images_processed, images_processed_date
    if date.today() != images_processed_date:
        images_processed = 0
        images_processed_date = date.today()
    if message.attachments:
        for attachment in message.attachments:
            if images_processed >= DAILY_IMAGE_LIMIT:
                print("Daily image limit reached")
                return
            if not attachment.content_type and not attachment.content_type.startswith("image/"):
                return
            print(f"Processing image from {message.author}: {attachment.filename}")
            images_processed += 1

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
    pass
    #msg = message.content
    #if "X/6:" in msg:
       # await message.channel.send(generate_wordle_roast(msg.split("X/6:")[1]))


# Create a client instance
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    if SELF_TEST:
        asyncio.create_task(run_self_test())


import glob as globmod


async def run_self_test():
    await asyncio.sleep(2)
    channel = client.get_channel(list(TEST_CHANNELS)[0])

    test_images = sorted(globmod.glob("testing/*.png"))
    if not test_images:
        print("FAIL: no test images found in testing/")
        await client.close()
        sys.exit(1)

    for img in test_images:
        print(f"TEST: sending {os.path.basename(img)}...")
        await channel.send(file=discord.File(img))

    # Wait for bot to process all images
    await asyncio.sleep(20)

    expected = len(test_images)
    got = self_test_results.get("scoreboard_count", 0)
    if got < expected:
        print(f"FAIL: bot responded to {got}/{expected} scoreboard images")
        await client.close()
        sys.exit(1)

    print(f"All tests passed ({got}/{expected} images)")
    await client.close()
    sys.exit(0)


self_test_results = {}

@client.event
async def on_message(message):
    if message.author == client.user:
        if SELF_TEST and message.channel.id in TEST_CHANNELS:
            if message.attachments:
                # let our own test images fall through to be processed
                pass
            else:
                # only count roast responses, not the "running smoothly" auto-reply
                if "scoreboard bot is running smoothly" not in message.content:
                    self_test_results["scoreboard_count"] = self_test_results.get("scoreboard_count", 0) + 1
                return
        else:
            return
    ch = message.channel.id
    if ch in TEST_CHANNELS:
        await message.channel.send("scoreboard bot is running smoothly from new machine")
        await check_wordle_fail(message)
    if ch in SCOREBOARD_CHANNELS:
        await check_scoreboard(message)
    if ch in WORDLE_CHANNELS:
        if message.author.id == 1211781489931452447:
            await check_wordle_fail(message)
    return
    

        

               
client.run(TOKEN)
