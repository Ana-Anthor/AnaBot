# Import the required modules
import discord
import os
from discord.ext import commands 
from dotenv import load_dotenv

# Create a Discord client instance and set the command prefix
intents = discord.Intents.all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)

# Retrieve token from the .env file
load_dotenv()
env = os.getenv("ENVIRONMENT")
if env == "TEST":
    token = os.getenv("TEST_TOKEN")
else:
    token = os.getenv("MAIN_TOKEN") 

# Set the confirmation message when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} in {env}-mode.')

# Set the commands for your bot
@bot.command()
async def list_command(ctx):
    cmds = [f"!{cmd}" for cmd in bot.commands]
    response = "You can use the following commands:\n" + "\n".join(cmds)
    await ctx.send(response)

@bot.command()
async def greet(ctx):
    response = 'Hello, I am your discord bot'
    await ctx.send(response)

@bot.command()
async def functions(ctx):
    response = 'I am a simple Discord chatbot! I will reply to your command!'
    await ctx.send(response)


bot.run(token)
