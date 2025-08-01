import pytest
import discord
from unittest.mock import AsyncMock, MagicMock
from discord.ext import commands
from cogs.commands import GeneralCommands

@pytest.fixture
def bot():
    bot = MagicMock(spec=commands.Bot)
    # Mock commands with explicit name attributes
    bot.commands = [
        MagicMock(spec=commands.Command),
        MagicMock(spec=commands.Command),
        MagicMock(spec=commands.Command),
        MagicMock(spec=commands.Command),
        MagicMock(spec=commands.Command)
    ]
    # Set name attributes explicitly
    command_names = ["greet", "list_command", "functions", "serverinfo", "myroles"]
    for cmd, name in zip(bot.commands, command_names):
        cmd.name = name
        cmd.__str__.return_value = name  # Ensure str(cmd) returns the name
    return bot

@pytest.fixture
def ctx(bot):
    ctx = MagicMock(spec=discord.ext.commands.Context)
    ctx.bot = bot
    ctx.guild = MagicMock(spec=discord.Guild)
    ctx.author = MagicMock(spec=discord.Member)
    ctx.send = AsyncMock()
    return ctx

@pytest.fixture
def cog(bot):
    return GeneralCommands(bot)

@pytest.mark.asyncio
async def test_list_command(bot, ctx, cog):
    await cog.list_command(cog, ctx)
    expected = "You can use the following commands:\n!greet\n!list_command\n!functions\n!serverinfo\n!myroles"
    ctx.send.assert_called_once_with(expected)

@pytest.mark.asyncio
async def test_greet(bot, ctx, cog):
    await cog.greet(cog, ctx)
    ctx.send.assert_called_once_with("Hello, I am your discord bot")

@pytest.mark.asyncio
async def test_functions(bot, ctx, cog):
    await cog.functions(cog, ctx)
    ctx.send.assert_called_once_with("I am a simple Discord chatbot! I will reply to your command!")

@pytest.mark.asyncio
async def test_serverinfo(bot, ctx, cog):
    ctx.guild.name = "TestServer"
    ctx.guild.member_count = 100
    await cog.serverinfo(cog, ctx)
    ctx.send.assert_called_once_with("Server name: TestServer\nTotal members: 100")

@pytest.mark.asyncio
async def test_myroles(bot, ctx, cog):
    role1 = MagicMock(spec=discord.Role)
    role1.name = "Role1"  # Set name as string
    role2 = MagicMock(spec=discord.Role)
    role2.name = "@everyone"
    role3 = MagicMock(spec=discord.Role)
    role3.name = "Role2"
    ctx.author.roles = [role1, role2, role3]
    await cog.myroles(cog, ctx)
    ctx.send.assert_called_once_with("Your roles: Role1, Role2")