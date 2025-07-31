# Import the required modules
import asyncio
import discord
import os
from discord.ext import commands 
from dotenv import load_dotenv

from onboarding import handle_member_join, handle_onboarding_message

# Create a Discord client instance and set the command prefix
intents = discord.Intents.all()
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

# A dictionay to temperary store onbording roles
onboarding_roles = {}

# When a member joins
@bot.event
async def on_member_join(member):
    await handle_member_join(member)

#When a member sends a message in waiting hall
@bot.event
async def on_message(message):
    await handle_onboarding_message(message,bot)
    
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

@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild
    response = f"Server name: {guild.name}\nTotal members: {guild.member_count}"
    await ctx.send(response)

@bot.command()
async def myroles(ctx):
    roles = [role.name for role in ctx.author.roles if role.name != "@everyone"]
    await ctx.send(f"Your roles: {', '.join(roles)}")

bot.run(token)
