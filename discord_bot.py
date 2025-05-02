import discord
from discord import app_commands
from discord.ext import commands
import json, os
from dotenv import load_dotenv

load_dotenv()

CONFIG_FILE = 'config.json'
DIFFICULTY_OPTIONS = ["easy", "medium", "hard"]

# Load config
with open(CONFIG_FILE, 'r') as f:
    config = json.load(f)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

class DifficultySelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=d.capitalize(), value=d) for d in DIFFICULTY_OPTIONS
        ]
        super().__init__(placeholder="Select Difficulty", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        config['difficulty'] = self.values[0]
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        await interaction.response.send_message(f"✅ Difficulty set to `{self.values[0]}`", ephemeral=True)

class DifficultyDropdown(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(DifficultySelect())

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Slash commands synced: {len(synced)}")
    except Exception as e:
        print(f"Error syncing commands: {e}")
    print(f"Bot is ready. Logged in as {bot.user}")

@bot.tree.command(name="setdifficulty", description="Set parsing difficulty for dab triggers")
async def set_difficulty(interaction: discord.Interaction):
    await interaction.response.send_message("Choose a difficulty:", view=DifficultyDropdown(), ephemeral=True)

@bot.tree.command(name="resetdifficulty", description="Reset to default difficulty")
async def reset_difficulty(interaction: discord.Interaction):
    if 'difficulty' in config:
        del config['difficulty']
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        await interaction.response.send_message("🔁 Difficulty reset to default.", ephemeral=True)
    else:
        await interaction.response.send_message("⚠️ Difficulty already at default.", ephemeral=True)

if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_TOKEN"))
