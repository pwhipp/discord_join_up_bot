# Discord join up bot

This is a discord bot that manages new people joining servers run as club collaborative environments.

When a new member joins, the bot automatically assigns them the Guest role and restricts them to #guest, then sends them a DM prompting for their club email address. 

Once the user replies, the bot verifies the email. If the address is valid and unused, it logs that email in #used-emails (to block multiple people using the same email), removes the Guest role, assigns Member or Admin based on staff status. 

Generates a unique nickname from the user’s name, posts a “Welcome @User!” message in #general, and sends a confirmation DM. If the user fails to give the bot a valid email after three failed attempts, the user remains in #guest and is asked to wait for an administrator manually verify them.

# Permissions

Must be given these permissions:
- Read Messages
- Send Messages
- Read Message History
- Manage Roles
- Manage Nicknames

The Join Up Bot role should be positioned above any of the roles it will assign or remove. In this case, this will be the admin role.


# Future plans

We will eventually have a visitior role where front-end users will receive one-time codes that grant temporary access to match-specific channels.

# Service notes

The service currently runs on qclub.au under the user discord_bot.

