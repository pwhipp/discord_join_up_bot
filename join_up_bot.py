from pathlib import Path
import yaml

import discord
from discord.ext import commands
import aiohttp


class JoinUpBot(commands.Bot):

    def __init__(self, *args, **kwds):

        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True

        super().__init__(*args, command_prefix="!", intents=intents, **kwds)
        self.config = load_config()

        self.failed_attempts = {}

    def run(self, token=None, **kwds) -> None:
        if token is None:
            token = self.bot_token
        super().run(token, **kwds)

    @property
    def bot_token(self):
        try:
            return self.config['bot']['token']
        except KeyError:
            raise Exception("No configured bot token")

    @property
    def allowed_guilds(self):
        guilds = set(self.config['guilds'].keys())
        if not guilds:
            raise Exception("No guilds configured")
        return guilds

    def is_guild_allowed(self, guild_id):
        return guild_id in self.allowed_guilds

    def find_member_guild(self, user_id):
        """
        Return the first allowed Guild where this user is a member,
        or None if we don’t recognize them.
        """
        for guild in self.guilds:
            if self.is_guild_allowed(guild.id) and guild.get_member(user_id):
                return guild
        return None

    async def on_ready(self):
        print(f"Ready as {self.user}. Allowed guilds: {self.allowed_guilds}")

    async def on_member_join(self, member):
        guild_id = member.guild.id
        if not self.is_guild_allowed(guild_id):
            return

        # All members join as a guest and get asked for their email
        guest_role = discord.utils.get(member.guild.roles, name="Guest")
        if guest_role:
            await member.add_roles(guest_role)
        guest_channel = discord.utils.get(member.guild.text_channels, name="guest")
        if guest_channel:
            await guest_channel.send(
                f"Welcome {member.mention}! To verify your club email, click on {self.user.mention} and send me your email address here."
            )
        try:
            await member.send(
                f"Hi {member.name}! Let’s get you verified. Please reply here with your club email address. "
            )
        except discord.Forbidden:
            print(f"Could not DM {member} for verification.")

    async def on_message(self, message):
        """
        We're looking for the guest member's response to our email question here.
        If the email corresponds to a member email, then we promote them to being a full member automatically.
        """
        # todo: There is a vulnerability here - everyone could use a single known email to become a full member.
        # - we should probably track the used emails so they can only be used once.
        # todo: What will happen with other chat in the guest channel?

        if message.author.bot:
            return None
        if message.guild:
            return await self.process_commands(message)

        guild = self.find_member_guild(message.author.id)
        if guild is None:
            return await self.process_commands(message)
        proposed_email = message.content.strip().lower()
        used_emails_channel = discord.utils.get(guild.text_channels, name="used-emails")
        if used_emails_channel:
            already_used = False
            async for log_message in used_emails_channel.history(limit=None):
                if log_message.content.lower() == proposed_email:
                    already_used = True
                    break

            if already_used:
                failures = self.failed_attempts.get(message.author.id, 0) + 1
                self.failed_attempts[message.author.id] = failures

                if failures >= 3:
                    await message.author.send(
                        "We are unable to verify your account automatically."
                        "Please return to the #guest channel and an administrator will assist you."
                    )
                    return None

                await message.author.send(
                    f" That email address has already been used. Please try again."
                )
                return None

        is_member, member_info = await self.is_member_email(message, guild.id)

        if is_member:
            used_emails_channel = discord.utils.get(guild.text_channels, name="used-emails")
            if used_emails_channel:
                await used_emails_channel.send(proposed_email)
            guild_member = guild.get_member(message.author.id)
            if guild_member is None:
                try:
                    guild_member = await guild.fetch_member(message.author.id)
                except discord.NotFound:
                    return None

            await self.set_member_roles(guild, guild_member, member_info)
            nickname = await self.set_nickname(guild_member, member_info)

            general_channel = discord.utils.get(guild.text_channels, name="general")
            if general_channel:
                await general_channel.send(
                    f"Welcome {guild_member.mention}!"
                )

                try:
                    await message.author.send(
                        f"You’ve been verified as **{nickname}**! Head over to {general_channel.mention} to get started."
                    )
                except discord.Forbidden:
                    print(f"Could not DM {message.author} confirmation.")

        return None

    async def is_member_email(self, message, guild_id):
        """
        Verify the supplied email address, returning True if the email belongs to a member
        """
        guild_settings = self.config['guilds'][guild_id]
        verify_endpoint = guild_settings.get("verify_endpoint")
        service_token = guild_settings.get("service_token")
        if not verify_endpoint or not service_token:
            return await message.channel.send("Configuration missing for this guild.")

        email = message.content.strip().lower()
        url = f"{verify_endpoint}?email={email}"
        headers = {"Authorization": f"Token {service_token}"}

        async with aiohttp.ClientSession(headers=headers) as sess:
            async with sess.get(url) as resp:
                if resp.status != 200:
                    return await message.channel.send("Verification service unavailable.")
                member_info = await resp.json()

        if member_info.get("verified"):
            return True, member_info
        else:
            await message.channel.send(
                "Sorry I can't match that email to an existing club member.")
            return False, member_info

    @staticmethod
    async def set_member_roles(guild, member, member_info):
        guest_role = discord.utils.get(guild.roles, name="Guest")
        member_role = discord.utils.get(guild.roles, name="Member")
        admin_role = discord.utils.get(guild.roles, name="Admin")

        if guest_role in member.roles:
            await member.remove_roles(guest_role)

        if member_info.get("is_staff"):
            if admin_role:
                await member.add_roles(admin_role)
        else:
            if member_role:
                await member.add_roles(member_role)

    @staticmethod
    async def set_nickname(member, member_info):
        firstname = member_info.get("first_name").strip()
        lastname = member_info.get("last_name").strip()
        base = (firstname[:1] + lastname).lower()
        count = sum(1 for m in member.guild.members if m.nick and m.nick.startswith(base))
        nickname = f"{base}{count + 1}" if count else base
        try:
            await member.edit(nick=nickname)
        except discord.Forbidden:
            print(f"Could not change nickname for {member}")
        return nickname


def load_config():
    config_path = Path(__file__).parent / 'config.yaml'
    with open(config_path, encoding="utf-8") as file:
        return yaml.safe_load(file)


if __name__ == "__main__":
    JoinUpBot().run()
