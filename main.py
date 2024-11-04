from dotenv import load_dotenv
from typing import Final
import os
import discord 
from discord import app_commands
from discord.ext import commands
load_dotenv()
token: Final[str] = os.getenv('token')
print(token)
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Event when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    # Sync commands to make sure they are available for use
    try:
        await bot.tree.sync()
        print("Slash commands have been synced!")
    except Exception as e:
        print(f"Error syncing commands: {e}")
    print('------')

# Slash command example
@bot.tree.command(name="hello", description="Says hello!")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello! This is a slash command.")

def main() -> None:
    bot.run(token=token)

if __name__ == '__main__':
    main()