import discord
import asyncio
import logging
#from storage.database import Database TODO: add database

class OnboardingManager:
    def __init__(self, guild):
        self.guild = guild
        self.onboarding_roles = {}  # Internal dictionary for role storage: self.db = DataBase()

    async def handle_member_join(self, member):
        logging.info("Bot permissions: %s", member.guild.me.guild_permissions)
        logging.info("Bot's highest role: %s (position %d)", member.guild.me.top_role.name, member.guild.me.top_role.position)
        logging.info("Member %s initial roles: %s", member.name, [role.name for role in member.roles])
        await self.add_role_new(member)
        await asyncio.sleep(10)  # Wait for Discord to sync
        member = await self.guild.fetch_member(member.id)
        logging.info("%s has roles: %s", member.name, [role.name for role in member.roles])

        # Store roles in dictionary
        original_roles = self.get_roles(member)
        self.onboarding_roles[member.id] = original_roles

        # Remove old roles excetpt "@everyone"
        await self.remove_all_roles(member, original_roles)
        #await self.add_role_new(member) TODO: remove

        member = await self.guild.fetch_member(member.id)
        logging.info("%s final roles: %s", member.name, [role.name for role in member.roles])
    

    async def handle_onboarding_message(self, member, channel):
        # Restore roles from dictionary
        roles = self.onboarding_roles.get(member.id, [])
        for role in roles:
            try:
                if role.name != "@everyone":  # Safety check
                    await member.add_roles(role)
                    logging.info("Restored role %s for %s", role.name, member.name)   
            except Exception as e:
                logging.error("Error restoring role %s for %s: %s", 
                             role.name, member.name, str(e))

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
                if role.name not in ("@everyone", "@New"):  # Safety check
                    await member.remove_roles(role)
                    logging.info("Removed role: {role.name}")
            except Exception as e:
                logging.info("Error removing role {role.name}: {e}")

    async def add_role_new(self, member):
        new_role = discord.utils.get(self.guild.roles, name="New")
        if not new_role:
            new_role = await self.guild.create_role(name="New", colour=discord.Colour.orange())
            logging.info("Created New role (position %d)", new_role.position)
            #TODO: add exception if making new roles is forbidden
        else:
            logging.info("Found existing New role (position %d)", new_role.position)
            if new_role.position >= self.guild.me.top_role.position:
                logging.error("Cannot assign New role to %s: role position %d >= bot's top role position %d", 
                                member.name, new_role.position, self.guild.me.top_role.position)
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
        new_role = discord.utils.get(self.guild.roles, name="New")
        if new_role and new_role in member.roles:
            try:
                await member.remove_roles(new_role)
                logging.info("Removed New role from %s", member.name)
                self.onboarding_roles.pop(member.id, None)
            except Exception as e:
                logging.error("Error removing New role from %s: %s", member.name, str(e))

    async def add_role_member(self, member):
        member_role = discord.utils.get(self.guild.roles, name="Member")
        if not member_role:
            member_role = await self.guild.create_role(name="Member", colour=discord.Colour.dark_green())
            logging.info("Created Member role (position %d)", member_role.position)
        await member.add_roles(member_role)
        logging.info("Added Member role to %s", member.name)

"""     # TODO: updata handle_member_join after db is added:
    async def handle_member_join(self, member):
        original_roles = self.get_roles(member)
        await self.db.store_roles(member.id, [role.id for role in original_roles]) """