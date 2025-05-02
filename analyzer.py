import openai
import os
import json
import asyncio
import discord
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

CONFIG_FILE = 'config.json'
KEYWORDS_FILE = 'trigger_keywords.json'

with open(CONFIG_FILE) as f:
    config = json.load(f)

with open(KEYWORDS_FILE) as f:
    keywords = json.load(f).get("default", [])

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

client = discord.Client(intents=discord.Intents.default())

async def send_discord_alert(text):
    await client.wait_until_ready()
    channel = client.get_channel(DISCORD_CHANNEL_ID)
    if channel:
        await channel.send(f"🔥 **DAB TRIGGERED** 🔥\n```{text}```")

# Entry for stream_monitor to call
async def analyze_and_alert(text):
    triggered = analyze_transcript(text) or keyword_triggered(text)
    if triggered:
        await send_discord_alert(text)
    return triggered

def analyze_transcript(text):
    difficulty = config.get("difficulty", "medium")

    prompt = f"""

You are a (your desire) assistant.
Evaluate the following transcript for x, y, or z.

Trigger a response if:
-
-

Difficulty = {difficulty.upper()}
Only respond with 'DAB' if one of these happens.

Transcript:
{text}

"""

    try:
        res = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        reply = res.choices[0].message.content.strip()
        return "DAB" in reply.upper()
    except Exception as e:
        print(f"[error] GPT failed: {e}")
        return False

def keyword_triggered(text):
    lowered = text.lower()
    return any(k.lower() in lowered for k in keywords)

# Example usage
if __name__ == "__main__":
    sample = "I just think Hamas is the real problem here."
    asyncio.run(client.start(DISCORD_TOKEN))
    asyncio.run(analyze_and_alert(sample))
