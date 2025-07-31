import discord
import asyncio
from discord.utils import get

onboarding_roles = {}

async def handle_member_join(member):
    # Check if its a bot
    if member.bot:
        return 
    
    try:
        member = await member.guild.fetch_member(member.id)
    except discord.NotFound:
        print("Member not found.")
        return
    
    manager = OnboardingManager(member.guild)

    # Waiting for discord to finish setting up onboarding roles
    await asyncio.sleep(10)
    member = await member.guild.fetch_member(member.id)
    print(f"{member.name} has these roles: {[role.name for role in member.roles]}")

    # Store member roles in dictionary with user-ID as key
    original_roles = manager.get_roles(member)
    onboarding_roles[member.id] = original_roles

    # Remove old roles and add the role New
    await manager.remove_all_roles(member, original_roles)
    await manager.add_role_new(member)

    member = await member.guild.fetch_member(member.id)
    print(f"{member.name} has these roles: {[role.name for role in member.roles]}")

async def handle_onboarding_message(message, bot):
    # Check if its a bot
    if message.author.bot:
        return 
    
    waiting_hall_id = 1399070297365155850
    welcome_channel = message.guild.get_channel(825128605868490815)
    member = message.author
    messageManager = WelcomeMessageManager(member)
    manager = OnboardingManager(member.guild)

    # Restor the roles from onboarding
    if message.channel.id == waiting_hall_id:

        if member.id in onboarding_roles:
            await manager.restore_onboarding_roles(member)
        
            # Remove the New role
            await manager.remove_role_new(member)
            
            await message.channel.send(f"{member.mention}, you're officially a part of the squad! 🔓 You now have full access. Enjoy your stay!")

            # Add the Member role
            await manager.add_role_member(member)
            await messageManager.send_welcome_message(member, welcome_channel)

    await bot.process_commands(message)

class OnboardingManager:
    def __init__(self, guild):
        self.guild = guild

    def get_roles(self, member):
        return [role for role in member.roles if role.name != "@everyone"]

    async def remove_all_roles(self, member, roles):
        for role in roles:
            try:
                await member.remove_roles(role)
                print(f"Removed role: {role.name}")
            except Exception as e:
                print(f"Error removing role {role.name}: {e}")

    async def restore_onboarding_roles(self, member):
        roles_to_restore = onboarding_roles.get(member.id, [])
        for role in roles_to_restore:
            try:
                await member.add_roles(role)
            except Exception as e:
                print(f"Restoring onboarding roles for {member.mention} failed: {e}")


    async def add_role_new(self, member):
        # See if the server has a role called "New"
        new_role = discord.utils.get(self.guild.roles, name="New")
        # If not, make the role
        if new_role is None:
            new_role = await self.guild.create_role(name="New", colour=discord.Colour.orange())
        # Give the New role to the new member
        await member.add_roles(new_role)
    
    async def remove_role_new(self, member):
        new_role = discord.utils.get(member.guild.roles, name="New")
        if new_role and new_role in member.roles:
            await member.remove_roles(new_role)

            onboarding_roles.pop(member.id, None)

    async def add_role_member(self, member):
        member_role = discord.utils.get(member.guild.roles, name="Member")
        if member_role:
            await member.add_roles(member_role)
        else:
            print("Member role not found.")

class WelcomeMessageManager:
    def __init__(self, member):
        self.member = member
        self.server_name = member.guild.name
        self.introduction_channel_id = 1151609579000561776
        self.information_channel_id = 1363917217309130963
        self.rules_channel_id = 1135973867001753711
        self.help_and_questions_channel_id = 1397028615446855780

    async def send_welcome_message(self, member, channel):
        
        # Send a welcome message in the welcome channel
        if channel:
            await channel.send(f"Welcome to {self.server_name}, {member.mention}! "
                            f"You’re now part of our awesome, chill gaming crew. 🎮 "
                            f"Drop by <#{self.introduction_channel_id}> and tell us about yourself. We love meeting our squad! "
                            f"Check <#{self.information_channel_id}> for server details and swing by <#{self.rules_channel_id}> to know what’s up. "
                            f"Got questions? Hit <#{self.help_and_questions_channel_id}>, and staff or members will help. "
                            f"If you spot us in voice chat, come say hi. We’d love to get to know you and game together!")
