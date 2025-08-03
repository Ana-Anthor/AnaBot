# cogs->commands.py
from discord.ext import commands
import logging
import discord

class GeneralCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def list_command(self, ctx):
        cmds = [f"!{cmd}" for cmd in self.bot.commands]
        logging.info(f"list_command executed by {ctx.author.name}")
        await ctx.send("You can use the following commands:\n" + "\n".join(cmds))

    @commands.command()
    async def greet(self, ctx):
        logging.info(f"greet command executed by {ctx.author.name}")
        await ctx.send('Hello, I am your discord bot')

    @commands.command()
    async def functions(self, ctx):
        logging.info(f"functions command executed by {ctx.author.name}")
        await ctx.send('I am a simple Discord chatbot! I will reply to your command!')

    @commands.command()
    async def serverinfo(self, ctx):
        guild = ctx.guild
        logging.info(f"serverinfo command executed by {ctx.author.name}")
        await ctx.send(f"Server name: {guild.name}\nTotal members: {guild.member_count}")

    @commands.command()
    async def myroles(self, ctx):
        roles = [role.name for role in ctx.author.roles if role.name != "@everyone"]
        logging.info(f"myroles command executed by {ctx.author.name}: {roles}")
        await ctx.send(f"Your roles: {', '.join(roles)}")

async def setup(bot):
    await bot.add_cog(GeneralCommands(bot))