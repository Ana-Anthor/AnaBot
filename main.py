# Import the required modules
import asyncio
import discord
import os
import logging
from discord.ext import commands 
from dotenv import load_dotenv

from onboarding import handle_member_join, handle_onboarding_message

# Set up logging to a file
logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s"
)

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
    logging.info(f'Logged in as {bot.user.name} in {env}-mode.')

# When a member joins
@bot.event
async def on_member_join(member):
    logging.info(f"Member joined: {member.name} ({member.id})")
    await handle_member_join(member)

#When a member sends a message in waiting hall
@bot.event
async def on_message(message):
    logging.info(f"Message received from {message.author.name} in channel {message.channel.id}")
    await handle_onboarding_message(message, bot) #TODO: all messages goes here, fix
    
# Set the commands for your bot
@bot.command()
async def list_command(ctx):
    cmds = [f"!{cmd}" for cmd in bot.commands]
    response = "You can use the following commands:\n" + "\n".join(cmds)
    logging.info(f"list_command executed by {ctx.author.name}")
    await ctx.send(response)

@bot.command()
async def greet(ctx):
    response = 'Hello, I am your discord bot'
    logging.info(f"greet command executed by {ctx.author.name}")
    await ctx.send(response)

@bot.command()
async def functions(ctx):
    response = 'I am a simple Discord chatbot! I will reply to your command!'
    logging.info(f"functions command executed by {ctx.author.name}")
    await ctx.send(response)

@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild
    response = f"Server name: {guild.name}\nTotal members: {guild.member_count}"
    logging.info(f"serverinfo command executed by {ctx.author.name}")
    await ctx.send(response)

@bot.command()
async def myroles(ctx):
    roles = [role.name for role in ctx.author.roles if role.name != "@everyone"]
    logging.info(f"myroles command executed by {ctx.author.name}: {roles}")
    await ctx.send(f"Your roles: {', '.join(roles)}")

bot.run(token)
