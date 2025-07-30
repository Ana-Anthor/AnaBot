# Import the required modules
import asyncio
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

# A dictionay to temperary store onbording roles
onboarding_roles = {}

# When a member joins
@bot.event
async def on_member_join(member):
    try:
        member = await member.guild.fetch_member(member.id)
    except discord.NotFound:
        print("Member not found.")
    
    # Waiting for discord to finish setting up onboarding roles
    await asyncio.sleep(3)
    member = await member.guild.fetch_member(member.id)
    print(f"{member.name} has these roles: {[role.name for role in member.roles]}")

    # Save current roles from onboarding, eksclude @everyone
    original_roles = [role for role in member.roles if role.name != "@everyone"]

    # Stor in dictionary with user-ID as key
    onboarding_roles[member.id] = original_roles

    # Remove old roles
    for role in original_roles:
        try:
            await member.remove_roles(role)
            print(f"Removed role: {role.name}")
        except Exception as e:
            print(f"Could not remove role {role.name}: {e}")

    # See if the server has a role called "New"
    new_role = discord.utils.get(member.guild.roles, name="New")

    # If not, make the role
    if new_role is None:
        new_role = await member.guild.create_role(name="New", colour=discord.Colour.orange())

    # Give the New role to the new member
    await member.add_roles(new_role)
    member = await member.guild.fetch_member(member.id)
    print(f"{member.name} has these roles: {[role.name for role in member.roles]}")

#When a member sends a message in waiting hall
@bot.event
async def on_message(message):
    # Check if its a bot
    if message.author.bot:
        return 

    #channels
    welcome_channel = message.guild.get_channel(825128605868490815)
    waiting_hall_id = 1399070297365155850
    introduction_channel_id = 1151609579000561776
    information_channel_id = 1363917217309130963
    rules_channel_id = 1135973867001753711
    help_and_questions_channel_id = 1397028615446855780

    # Restor the roles from onboarding
    if message.channel.id == waiting_hall_id:
        member = message.author
        server_name = member.guild.name

        if member.id in onboarding_roles:
            roles_to_restore = onboarding_roles[member.id]
            for role in roles_to_restore:
                await member.add_roles(role)
            
            # Remove the New role
            new_role = discord.utils.get(member.guild.roles, name="New")
            if new_role and new_role in member.roles:
                await member.remove_roles(new_role)

            onboarding_roles.pop(member.id, None)
            
            await message.channel.send(f"{member.mention}, you're officially a part of the squad! 🔓 You now have full access. Enjoy your stay!")

            # Add the Member role
            member_role = discord.utils.get(member.guild.roles, name="Member")
            if member_role:
                await member.add_roles(member_role)
            else:
                print("Member role not found.")


            # Send a welcome message in the welcome channel
            if welcome_channel:
                await welcome_channel.send(f"Welcome to {server_name}, {member.mention}! "
                                f"You’re now part of our awesome, chill gaming crew. 🎮 "
                                f"Drop by <#{introduction_channel_id}> and tell us about yourself. We love meeting our squad! "
                                f"Check <#{information_channel_id}> for server details and swing by <#{rules_channel_id}> to know what’s up. "
                                f"Got questions? Hit <#{help_and_questions_channel_id}>, and staff or members will help. "
                                f"If you spot us in voice chat, come say hi. We’d love to get to know you and game together!")

    await bot.process_commands(message)

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
