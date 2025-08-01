import discord
from utils.onboarding_manager import OnboardingManager
from utils.welcome_manager import WelcomeMessageManager
from utils.config import load_config
from discord.ext import commands


class Onboarding(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = load_config()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return
        try:
            member = await member.guild.fetch_member(member.id)
            manager = OnboardingManager(member.guild)
            await manager.handle_member_join(member)
        except discord.NotFound:
            print("Member not found.")


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.channel.id == self.config['waiting_hall_id']:
            manager = OnboardingManager(message.guild)
            welcome_manager = WelcomeMessageManager(message.author)
            await manager.handle_onboarding_message(message.author, message.channel)
            welcome_channel = message.guild.get_channel(self.config['welcome_channel_id'])
            await welcome_manager.send_welcome_message(message.author, welcome_channel)
            await self.bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(Onboarding(bot))

