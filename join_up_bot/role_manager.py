import discord
from .nickname import generate_nickname


async def set_member_roles(guild, member, member_info):
    guest_role = discord.utils.get(guild.roles, name="Guest")
    member_role = discord.utils.get(guild.roles, name="Member")
    admin_role = discord.utils.get(guild.roles, name="Admin")

    if guest_role in member.roles:
        await member.remove_roles(guest_role)

    if member_info.get("is_staff") and admin_role:
        await member.add_roles(admin_role)
    elif member_role:
        await member.add_roles(member_role)


async def set_nickname(member, member_info):
    nickname = generate_nickname(member_info, member.guild.members)
    try:
        await member.edit(nick=nickname)
    except discord.Forbidden:
        print(f"Could not change nickname for {member}")
    return nickname
