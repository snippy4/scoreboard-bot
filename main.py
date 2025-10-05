import os
import io
import re
import discord
from dotenv import load_dotenv
from PIL import Image
import pytesseract


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
            if attachment.content_type and attachment.content_type.startswith("image/"):
                print(f"📸 Processing image from {message.author}: {attachment.filename}")

                # Download image
                image_bytes = await attachment.read()
                image = Image.open(io.BytesIO(image_bytes))

                # OCR: extract text
                text = pytesseract.image_to_string(image)
                print("🔎 OCR result:\n", text)

                # Try to parse player names and kills from text
                # This regex looks for: name (word chars) then kills as number
                pattern = r"([A-Za-z0-9_]+)\s+(\d+)\s*/\s*\d+\s*/\s*\d+"
                players = re.findall(pattern, text)

                if len(players) >= 2:
                    top_player, bottom_player = players[0], players[1]
                    top_name, top_kills = top_player[0], int(top_player[1])
                    bottom_name, bottom_kills = bottom_player[0], int(bottom_player[1])

                    print(f"👤 Top: {top_name} ({top_kills} kills)")
                    print(f"👤 Bottom: {bottom_name} ({bottom_kills} kills)")

                    if top_kills < bottom_kills:
                        await message.channel.send(
                            f"⚠️ Detected: **{top_name}** has fewer kills ({top_kills}) than **{bottom_name}** ({bottom_kills})!"
                        )
                else:
                    print("❌ Could not parse player info from OCR text.")
client.run(TOKEN)
