import discord
import asyncio
#from storage.database import Database TODO: add database

class OnboardingManager:
    def __init__(self, guild):
        self.guild = guild
        self.onboarding_roles = {}  # Internal dictionary for role storage: self.db = DataBase()

    async def handle_member_join(self, member):
        await asyncio.sleep(10)  # Wait for Discord to sync
        member = await self.guild.fetch_member(member.id)
        print(f"{member.name} has these roles: {[role.name for role in member.roles]}")

        # Store roles in dictionary, excluding @everyone
        original_roles = self.get_roles(member)
        self.onboarding_roles[member.id] = original_roles

        # Remove old roles and add "New"
        await self.remove_all_roles(member, original_roles)
        await self.add_role_new(member)

        member = await self.guild.fetch_member(member.id)
        print(f"{member.name} has these roles: {[role.name for role in member.roles]}")

    async def handle_onboarding_message(self, member, channel):
        # Restore roles from dictionary
        roles = self.onboarding_roles.get(member.id, [])
        for role in roles:
            try:
                if role.name != "@everyone":  # Safety check
                    await member.add_roles(role)
            except Exception as e:
                print(f"Restoring role {role.name} failed: {e}")

        # Remove "New" role
        await self.remove_role_new(member)

        # Add "Member" role
        await self.add_role_member(member)

        await channel.send(f"{member.mention}, you're officially a part of the squad! 🔓 You now have full access. Enjoy your stay!")

    def get_roles(self, member):
        # Exclude @everyone as it's a default role that shouldn't be stored or manipulated
        return [role for role in member.roles if role.name != "@everyone"]

    async def remove_all_roles(self, member, roles):
        for role in roles:
            try:
                if role.name != "@everyone":  # Safety check
                    await member.remove_roles(role)
                    print(f"Removed role: {role.name}")
            except Exception as e:
                print(f"Error removing role {role.name}: {e}")

    async def add_role_new(self, member):
        new_role = discord.utils.get(self.guild.roles, name="New")
        if not new_role:
            new_role = await self.guild.create_role(name="New", colour=discord.Colour.orange())
        await member.add_roles(new_role)

    async def remove_role_new(self, member):
        new_role = discord.utils.get(self.guild.roles, name="New")
        if new_role and new_role in member.roles:
            await member.remove_roles(new_role)
            self.onboarding_roles.pop(member.id, None)

    async def add_role_member(self, member):
        member_role = discord.utils.get(self.guild.roles, name="Member")
        if not member_role:
            member_role = await self.guild.create_role(name="Member", colour=discord.Colour.dark_green())
        await member.add_roles(member_role)

"""     # TODO: updata handle_member_join after db is added:
    async def handle_member_join(self, member):
        original_roles = self.get_roles(member)
        await self.db.store_roles(member.id, [role.id for role in original_roles]) """