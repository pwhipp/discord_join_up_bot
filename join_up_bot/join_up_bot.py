import discord
from discord.ext import commands

from .config import load_config
from .rate_limiter import RateLimiter
from .events import on_ready, on_member_join, on_message


class JoinUpBot(commands.Bot):
    on_ready = on_ready
    on_member_join = on_member_join
    on_message = on_message

    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

        self.config = load_config()
        self.rate_limiter = RateLimiter()

    def run(self, token=None, **kwds):
        if token is None:
            token = self.bot_token
        super().run(token, **kwds)

    @property
    def bot_token(self):
        try:
            return self.config["bot"]["token"]
        except KeyError:
            raise Exception("No configured bot token")

    @property
    def allowed_guilds(self):
        guilds = set(self.config["guilds"].keys())
        if not guilds:
            raise Exception("No guilds configured")
        return guilds

    def is_guild_allowed(self, guild_id):
        return guild_id in self.allowed_guilds

    def find_member_guild(self, user_id):
        for guild in self.guilds:
            if self.is_guild_allowed(guild.id) and guild.get_member(user_id):
                return guild
        return None
