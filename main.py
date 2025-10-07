import os
import io
import re
import discord
from dotenv import load_dotenv
from PIL import Image
from scoreboard_to_data import ValorantScoreboardParser


# Load your bot token from .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Replace with the channel ID you want to read messages from
TARGET_CHANNEL_ID = 1424379611692924998  # 👈 your channel ID as an integer

# Enable message content intent (required to read messages)
intents = discord.Intents.default()
intents.message_content = True

# Create a client instance
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user} (ID: {client.user.id})")
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
            print(f"📸 Processing image from {message.author}: {attachment.filename}")

            # Download image
            image_bytes = await attachment.read()
            image = Image.open(io.BytesIO(image_bytes))
            image.save('image.png')
            scorebaording = ValorantScoreboardParser('image.png')
            scoreboarded = scorebaording.find_scoreboarding()
            print(scoreboarded)
               
client.run(TOKEN)
