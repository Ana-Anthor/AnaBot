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

    @commands.Cog.listener()
    async def on_member_join(self, member):
        logging.info(f"Member joined: {member.name} ({member.id})")
        if member.bot:
            return
        try:
            member = await member.guild.fetch_member(member.id)
            manager = OnboardingManager(member.guild)
            await manager.handle_member_join(member)
        except discord.NotFound:
            logging.info("Member not found.")


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            logging.info("Ignoring bot message: %s", message.author.name)
            return
        if message.channel.id == self.config['start_here_channel_id']:
            logging.info(f"Message received from {message.author.name} in channel {message.channel.name} with id {message.channel.id}")
            logging.info("%s has roles: %s", message.author.name, [role.name for role in message.author.roles])
            manager = OnboardingManager(message.guild)
            welcome_manager = WelcomeMessageManager(message.author)
            await manager.handle_onboarding_message(message.author, message.channel)
            welcome_channel = message.guild.get_channel(self.config['welcome_channel_id'])
            await welcome_manager.send_welcome_message(message.author, welcome_channel)
            await self.bot.process_commands(message)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if after.id in self.pending_onboarding and after.flags.completed_onboarding and not before.flags.completed_onboarding:
            logging.info(f"{after.name} has finished onboarding")
            manager = OnboardingManager(after.guild)
            await manager.handle_onboarding_roles(after)
            del self.pending_onboarding[after.id]  # Remove from pending
            logging.info(f"Removed {after.name} from pending_onboarding")

async def setup(bot):
    await bot.add_cog(Onboarding(bot))