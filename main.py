# main.py
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import logging
from utils.config import load_config

# Set up logging to a file
logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s"
)

# Load environment variables
load_dotenv()
config = load_config()

# Initialize bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=config['prefix'], intents=intents)

# Load cogs
async def load_cogs():
    for cog in ['cogs.onboarding', 'cogs.commands']:
        try:
            await bot.load_extension(cog)
            print(f'Loaded cog: {cog}')
        except Exception as e:
            print(f'Failed to load cog {cog}: {e}')

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user.name} in {config['environment']}-mode.')

# Run bot
async def main():
    await load_cogs()
    await bot.start(config['token'])

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nThe bot was terminated using Ctrl + C.")
