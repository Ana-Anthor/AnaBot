# onboarding.py
import logging
import discord
import asyncio
import time
from discord.utils import get

# Set up logging to a file
logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s"
)

onboarding_roles = {}

async def handle_member_join(member):
    # Check if its a bot
    if member.bot:
        logging.info("Ignoring bot join: %s", member.name)
        return 
    try:
        member = await member.guild.fetch_member(member.id)
    except discord.NotFound:
        logging.error("Member not found: %s", member.id)
        return
    
    manager = OnboardingManager(member.guild)
    
    # Log environment and process info 
    logging.info("Bot permissions: %s", member.guild.me.guild_permissions)
    logging.info("Bot's highest role: %s (position %d)", member.guild.me.top_role.name, member.guild.me.top_role.position)
    logging.info("Member %s initial roles: %s", member.name, [r.name for r in member.roles])
    # Poll roles to ensure onboarding completes
    start_time = time.time()
    initial_roles = len(member.roles)
    for _ in range(30):
        await asyncio.sleep(1)
        updated_member = await member.guild.fetch_member(member.id)
        if len(updated_member.roles) == initial_roles:
            break
        member = updated_member
        initial_roles = len(updated_member.roles)
    logging.info("Role polling took %s seconds for %s", time.time() - start_time, member.name)
    logging.info("%s has roles: %s", member.name, [r.name for r in member.roles])
    # Store member roles in dictionary with user-ID as key
    original_roles = manager.get_roles(member)
    logging.info("Storing roles for %s: %s", member.name, [r.name for r in original_roles])
    onboarding_roles[member.id] = original_roles
    # Remove old roles and add the role New
    await manager.remove_all_roles(member, original_roles)
    await manager.add_role_new(member)
    member = await member.guild.fetch_member(member.id)
    logging.info("%s final roles: %s", member.name, [r.name for r in member.roles])
    
async def handle_onboarding_message(message, bot):
    # Check if its a bot
    if message.author.bot:
        logging.info("Ignoring bot-join: %s", message.author.name)
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
                start_time = time.time()
                await member.remove_roles(role)
                logging.info("Removed role %s for %s in %s seconds", 
                            role.name, member.name, time.time() - start_time)
                await asyncio.sleep(0.5)  # Delay to avoid rate limits
            except discord.HTTPException as e:
                logging.error("HTTP error removing role %s for %s: %s", 
                             role.name, member.name, str(e))
            except Exception as e:
                logging.error("Error removing role %s for %s: %s", 
                             role.name, member.name, str(e))

    async def restore_onboarding_roles(self, member):
        roles_to_restore = onboarding_roles.get(member.id, [])
        for role in roles_to_restore:
            try:
                await member.add_roles(role)
                logging.info("Restored role %s for %s", role.name, member.name)   
            except Exception as e:
                logging.error("Error restoring role %s for %s: %s", 
                             role.name, member.name, str(e))


    async def add_role_new(self, member):
        # See if the server has a role called "New"
        new_role = discord.utils.get(self.guild.roles, name="New")
        # If the role New alreadu excists
        if new_role:
            logging.info("Found existing New role (position %d)", new_role.position)
            if new_role.position >= self.guild.me.top_role.position:
                logging.error("Cannot assign New role to %s: role position %d >= bot's top role position %d", 
                                member.name, new_role.position, self.guild.me.top_role.position)
                return
        # Else, make the role
        else:
            try:
                new_role = await self.guild.create_role(name="New", colour=discord.Colour.orange())
                logging.info("Created New role (position %d)", new_role.position)
            except discord.Forbidden:
                logging.error("Error creating New role for %s: Missing manage_roles permission", member.name)
                return
            except discord.HTTPException as e:
                logging.error("HTTP error creating New role for %s: %s", member.name, str(e))
                return
            except Exception as e:
                logging.error("Error creating New role: %s", str(e))
                return
        try:
            await member.add_roles(new_role)
            logging.info("Added New role to %s", member.name)
        except discord.Forbidden:
            logging.error("Error adding New role to %s: Missing manage_roles permission or role hierarchy issue", member.name)
        except discord.HTTPException as e:
            logging.error("HTTP error adding New role to %s: %s", member.name, str(e))
        except Exception as e:
            logging.error("Error adding New role to %s: %s", member.name, str(e))

    async def remove_role_new(self, member):
        new_role = discord.utils.get(member.guild.roles, name="New")
        if new_role and new_role in member.roles:
            try:
                await member.remove_roles(new_role)
                logging.info("Removed New role from %s", member.name)
                onboarding_roles.pop(member.id, None)
            except Exception as e:
                logging.error("Error removing New role from %s: %s", member.name, str(e))

    async def add_role_member(self, member):
        member_role = discord.utils.get(member.guild.roles, name="Member")
        if member_role:
            try:
                await member.add_roles(member_role)
                logging.info("Added Member role to %s", member.name)
            except Exception as e:
                logging.error("Error adding Member role to %s: %s", member.name, str(e))
        else:
            logging.error("Member role not found")

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
            try:
                await channel.send(f"Welcome to {self.server_name}, {member.mention}! "
                                f"You’re now part of our awesome, chill gaming crew. 🎮 "
                                f"Drop by <#{self.introduction_channel_id}> and tell us about yourself. We love meeting our squad! "
                                f"Check <#{self.information_channel_id}> for server details and swing by <#{self.rules_channel_id}> to know what’s up. "
                                f"Got questions? Hit <#{self.help_and_questions_channel_id}>, and staff or members will help. "
                                f"If you spot us in voice chat, come say hi. We’d love to get to know you and game together!")
                logging.info("Sent welcome message for %s", member.name)
            except Exception as e:
                logging.error("Error sending welcome message for %s: %s", member.name, str(e))
