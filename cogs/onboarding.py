# cogs->onboarding.py
import discord
from utils.onboarding_manager import OnboardingManager
from utils.welcome_manager import WelcomeMessageManager
from utils.config import load_config
from discord.ext import commands
import logging

class Onboarding(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = load_config()
        self.pending_onboarding = {}
        self.onboarding_roles = {}

#1
    @commands.Cog.listener()
    async def on_member_join(self, member):
        logging.info(f"Member joined: {member.name} ({member.id})")
        if member.bot:
            logging.info("Member vas a bot.")
            return
        try:
            member = await member.guild.fetch_member(member.id)
            manager = OnboardingManager(member.guild, self.onboarding_roles)
            self.pending_onboarding[member.id] = True # The onbording flag is set to true
            logging.info(f"{member.name} waiting for onboarding")
            logging.info("Bot permissions: %s", member.guild.me.guild_permissions)
            logging.info("Bot's highest role: %s (position %d)", member.guild.me.top_role.name, member.guild.me.top_role.position)
            logging.info("Member %s initial roles: %s", member.name, [role.name for role in member.roles])
            await manager.add_role_new(member) #1a
            start_here_channel = member.guild.get_channel(self.config['start_here_channel_id'])
            await manager.send_verification_question(member, start_here_channel) #1b

        except discord.NotFound:
            logging.info("Member not found.")
        except Exception as e:
            logging.error(f"Error in on_member_join for {member.name}: {e}")

#2
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if after.id in self.pending_onboarding and after.flags.completed_onboarding and not before.flags.completed_onboarding:
            logging.info(f"{after.name} has finished onboarding")
            manager = OnboardingManager(after.guild, self.onboarding_roles)
            await manager.pemporary_store_and_remove_onboarding_roles(after) #2a
            del self.pending_onboarding[after.id]  # Remove from pending
            logging.info(f"Removed {after.name} from pending_onboarding")

#3
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            logging.info("Ignoring bot message: %s", message.author.name)
            return
        if message.channel.id == self.config['start_here_channel_id']:
            logging.info(f"{message.author.name} answerd to the verification question in channel {message.channel.name} with id {message.channel.id}")
            manager = OnboardingManager(message.guild, self.onboarding_roles)
            welcome_manager = WelcomeMessageManager(message.author)
            await manager.restore_onboarding_roles(message.author, message.channel) #3a
            await manager.remove_role_new(message.author) #3b
            await manager.add_role_member(message.author) #3c

            await message.channel.send(f"{message.author.mention}, you're officially a part of the squad! 🔓 You now have full access. Enjoy your stay!")

            welcome_channel = message.guild.get_channel(self.config['welcome_channel_id'])
            await welcome_manager.send_welcome_message(message.author, welcome_channel)
            await self.bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(Onboarding(bot))