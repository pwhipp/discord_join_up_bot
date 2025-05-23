import aiohttp


async def verify_email(message, guild_settings):
    endpoint = guild_settings.get("verify_endpoint")
    token = guild_settings.get("service_token")
    if not endpoint or not token:
        await message.channel.send("Configuration missing for this guild.")
        return False, {}

    email = message.content.strip().lower()
    url = f"{endpoint}?email={email}"
    headers = {"Authorization": f"Token {token}"}

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            if response.status != 200:
                await message.channel.send("Verification service unavailable.")
                return False, {}
            info = await response.json()

    if info.get("verified"):
        return True, info
    await message.channel.send("Sorry I can't match that email to an existing club member.")
    return False, info
