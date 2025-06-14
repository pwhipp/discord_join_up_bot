import discord
class RateLimiter:

    max_attempts = 3

    def __init__(self):
        self.failed_attempts = {}

    def add_attempt(self, user_id):
        count = self.failed_attempts.get(user_id, 0) + 1
        self.failed_attempts[user_id] = count
        return count

    def reset(self, user_id):
        self.failed_attempts.pop(user_id, None)

    def get_attempts(self, user_id):
        return self.failed_attempts.get(user_id, 0)

    async def record_attempts(self, user, verification_channel, admin_role):
        count = self.add_attempt(user.id)
        if count >= self.max_attempts:
            guild = verification_channel.guild
            member = await guild.fetch_member(user.id)
            guest = discord.utils.get(guild.roles, name="Guest")
            unverified = discord.utils.get(guild.roles, name="Unverified")
            if guest and unverified:
                await member.remove_roles(guest)
                await member.add_roles(unverified)

            await user.send(
                f"We are unable to verify your account automatically. "
                f"Please return to {verification_channel.mention} and an administrator will assist you."
            )
            await verification_channel.send(
                f"{admin_role.mention} Hey {user.mention}, "
                f"we can't verify you as a member. Can you help me confirm your identity?"
            )
            return True

        return False