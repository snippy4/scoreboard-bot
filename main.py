import os
import io
import re
import discord
from dotenv import load_dotenv
from PIL import Image
from scoreboard_to_data import ValorantScoreboardParser
from openai import OpenAI

# Load environment variables
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

ALLOWED_NAMES = {
    'snippy': '345254471753924611',
    'masochist': '294868726313123870',
    'sweetcorn': '370258922868572172',
    'switch': '610223436522061853',
    'betajumper': '364856743441989633',
    'gutz': '362310474798202881',
    'sadist': '452533933452689439',
    'glitch': '754721639010140272',
    'ginger': '406485851699281936',
    'papi': '77074956743086080',
    'aiyeo': '342433750409281536',
}

# DeepSeek client (OpenAI-compatible)
deepseek_client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# Channel IDs
MOMENTS_CHANNEL_ID = 1065429100199686234
TEST_CHANNEL_ID = 1424379611692924998
SPAM_CHANNEL_ID = 1194066107821195355

# Discord intents
intents = discord.Intents.default()
intents.message_content = True


def generate_valorant_roast(scoreboarded_pairs):
    pairs_text = []
    for p1, p2 in scoreboarded_pairs:
        pairs_text.append(
            f"<@{ALLOWED_NAMES[p2['name'].lower()]}> "
            f"({p2['score']} score, {p2['kills']} kills) got scoreboarded "
            f"by <@{ALLOWED_NAMES[p1['name'].lower()]}> "
            f"({p1['score']} score, {p1['kills']} kills)"
        )

    prompt = (
        f"Write a quick funny roast for this situation:\n{pairs_text}\n\n"
        "This is a friendly inside joke. Be savage but funny. "
        "Talk like a chronically online 18 year old. "
        "Use informal language, text speak, and profanity if you want. "
        "Do not overuse punctuation. "
        "Only output ONE Discord-ready message."
    )

    response = deepseek_client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
    )

    return response.choices[0].message.content


def generate_wordle_roast(people):
    prompt = (
        f"{people.split(' ')} failed the Wordle yesterday.\n\n"
        "Write a short funny roast about how badly they failed. "
        "This is a friendly inside joke. "
        "Use profanity, insults, and realistic text speak. "
        "Talk like a chronically online 18 year old. "
        "Only output ONE Discord-ready message."
    )

    response = deepseek_client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
    )

    return response.choices[0].message.content


async def check_scoreboard(message):
    if not message.attachments:
        return

    for attachment in message.attachments:
        if not attachment.content_type or not attachment.content_type.startswith("image/"):
            return

        print(f"Processing image from {message.author}: {attachment.filename}")

        image_bytes = await attachment.read()
        image = Image.open(io.BytesIO(image_bytes))
        image.save("image.png")

        scoreboard = ValorantScoreboardParser("image.png")
        scoreboarded = scoreboard.find_scoreboarding()

        scoreboarded = [
            (p1, p2)
            for p1, p2 in scoreboarded
            if p1["name"].lower() in ALLOWED_NAMES
            and p2["name"].lower() in ALLOWED_NAMES
        ]

        print(scoreboarded)

        if scoreboarded:
            roast = generate_valorant_roast(scoreboarded)
            await message.channel.send(roast)
            await message.add_reaction("<:snippy:1208470366909890662>")


async def check_wordle_fail(message):
    if "X/6:" in message.content:
        await message.channel.send(
            generate_wordle_roast(message.content.split("X/6:")[1])
        )


# Discord client
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.id == TEST_CHANNEL_ID:
        await message.channel.send("scoreboard bot is running smoothly on new host")
        await check_scoreboard(message)
        await check_wordle_fail(message)

    if message.channel.id == MOMENTS_CHANNEL_ID:
        await check_scoreboard(message)

    if message.channel.id == SPAM_CHANNEL_ID:
        if message.author.id == 1211781489931452447:
            await check_wordle_fail(message)


client.run(TOKEN)
