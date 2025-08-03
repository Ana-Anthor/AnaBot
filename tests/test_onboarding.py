import pytest
import discord
from unittest.mock import AsyncMock, MagicMock
from utils.onboarding_manager import OnboardingManager

@pytest.fixture
def mock_guild():
    guild = MagicMock(spec=discord.Guild)
    guild.create_role = AsyncMock()  # Use AsyncMock for async method
    guild.fetch_member = AsyncMock()
    return guild

@pytest.fixture
def mock_member(mock_guild):
    member = MagicMock(spec=discord.Member)
    member.guild = mock_guild
    member.id = 12345
    member.bot = False
    member.roles = []
    member.add_roles = AsyncMock()  # Use AsyncMock for async method
    return member

@pytest.mark.asyncio
async def test_add_role_new(mock_guild, mock_member, monkeypatch):
    manager = OnboardingManager(mock_guild)
    new_role = MagicMock(spec=discord.Role, name="New")
    
    # Mock discord.utils.get to return None
    monkeypatch.setattr("discord.utils.get", MagicMock(return_value=None))
    mock_guild.create_role.return_value = new_role

    await manager.add_role_new(mock_member)

    mock_guild.create_role.assert_called_once_with(name="New", colour=discord.Colour.orange())
    mock_member.add_roles.assert_called_once_with(new_role)

@pytest.mark.asyncio
async def test_handle_member_join(mock_guild, mock_member, monkeypatch):
    manager = OnboardingManager(mock_guild)
    role = MagicMock(spec=discord.Role, name="TestRole")
    mock_member.roles = [role]
    mock_guild.fetch_member.return_value = mock_member
    monkeypatch.setattr("discord.utils.get", MagicMock(return_value=None))
    
    await manager.handle_member_join(mock_member)

    assert manager.onboarding_roles[mock_member.id] == [role]

@pytest.mark.asyncio
async def test_get_roles_excludes_everyone(mock_guild, mock_member):
    manager = OnboardingManager(mock_guild)
    everyone_role = MagicMock(spec=discord.Role)
    everyone_role.name = "@everyone"
    other_role = MagicMock(spec=discord.Role)
    other_role.name = "OtherRole"

    mock_member.roles = [everyone_role, other_role]

    roles = manager.get_roles(mock_member)
    print(f"Her er testen: ")

    assert "@everyone" not in [r.name for r in roles]
    assert "OtherRole" in [r.name for r in roles]