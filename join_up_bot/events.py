import discord
from .email_verification import verify_email
from .role_manager import set_member_roles, set_nickname
from .rate_limiter import RateLimiter


async def on_ready(self):
    print(f"Logged in as {self.user} (ID: {self.user.id})")
    for guild in self.guilds:
        if not self.is_guild_allowed(guild.id):
            continue
        print(f"\nAllowed guild: {guild.name} (ID: {guild.id})")
        for channel in guild.text_channels:
            perms = channel.permissions_for(guild.me)
            if perms.read_messages and perms.send_messages:
                print(f"Listening in: #{channel.name} (ID: {channel.id})")


async def on_member_join(self, member):
    guild_id = member.guild.id
    if not self.is_guild_allowed(guild_id):
        return

    guest_role = discord.utils.get(member.guild.roles, name="Guest")
    if guest_role:
        await member.add_roles(guest_role)

    guest_channel = discord.utils.get(member.guild.text_channels, name="guest")
    if guest_channel:
        await guest_channel.send(
            f"Welcome {member.mention}! To verify your club email, click on {self.user.mention} "
            f"and send me your email address here."
        )

    try:
        await member.send(
            f"Hi {member.name}! Let’s get you verified. Please reply here with your club email address."
        )
    except discord.Forbidden:
        print(f"Could not DM {member} for verification.")


async def on_message(self, message):
    if message.author.bot:
        return None
    if message.guild:
        return await self.process_commands(message)

    if self.rate_limiter.get_attempts(message.author.id) >= RateLimiter.max_attempts:
        return None
    guild = self.find_member_guild(message.author.id)
    if guild is None:
        return await self.process_commands(message)

    admin_role = discord.utils.get(guild.roles, name="Admin")
    guest_channel = discord.utils.get(guild.text_channels, name="guest")
    general_channel = discord.utils.get(guild.text_channels, name="general")
    proposed_email = message.content.strip().lower()
    used_emails_channel = discord.utils.get(guild.text_channels, name="used-emails")

    if used_emails_channel:
        async for log_message in used_emails_channel.history(limit=None):
            if log_message.content.lower() == proposed_email:
                await message.author.send("That email address has already been used. Please try again.")
                if await self.rate_limiter.record_attempts(message.author, guest_channel, admin_role):
                    return None
                return None

    guild_settings = self.config["guilds"][guild.id]
    is_member, member_info = await verify_email(message, guild_settings)

    if is_member:
        self.rate_limiter.reset(message.author.id)
        if used_emails_channel:
            await used_emails_channel.send(proposed_email)

        guild_member = guild.get_member(message.author.id)
        if guild_member is None:
            try:
                guild_member = await guild.fetch_member(message.author.id)
            except discord.NotFound:
                return None

        await set_member_roles(guild, guild_member, member_info)
        nickname = await set_nickname(guild_member, member_info)

        if general_channel:
            await general_channel.send(f"Welcome {guild_member.mention}!")
            try:
                await message.author.send(
                    f"You’ve been verified as **{nickname}**! Head over to {general_channel.mention} to get started."
                )
            except discord.Forbidden:
                print(f"Could not DM confirmation to {message.author}.")
    else:
        if await self.rate_limiter.record_attempts(message.author, guest_channel, admin_role):
            return None

    return None
