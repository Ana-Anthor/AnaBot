import discord
from utils.config import load_config

class WelcomeMessageManager:
    def __init__(self, member):
        self.member = member
        self.server_name = member.guild.name
        self.config = load_config()

    async def send_welcome_message(self, member, channel):
        if channel:
            await channel.send(
                f"Welcome to {self.server_name}, {member.mention}! "
                f"You’re now part of our awesome, chill gaming crew. 🎮 "
                f"Drop by <#{self.config['introduction_channel_id']}> and tell us about yourself. "
                f"Check <#{self.config['information_channel_id']}> for server details and "
                f"swing by <#{self.config['rules_channel_id']}> to know what’s up. "
                f"Got questions? Hit <#{self.config['help_channel_id']}>, and staff or members will help. "
                f"If you spot us in voice chat, come say hi. We’d love to get to know you and game together!"
            )