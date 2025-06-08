# Discord join up bot

This is a discord bot that manages new people joining servers run as club collaborative environments.

When a new member joins, the bot automatically assigns them the Guest role and restricts them to #guest, then sends them a DM prompting for their club email address. 

Once the user replies, the bot verifies the email. If the address is valid and unused, it logs that email in #used-emails (to block multiple people using the same email), removes the Guest role, assigns Member or Admin based on staff status. 

Generates a unique nickname from the user’s name, posts a “Welcome @User!” message in #general, and sends a confirmation DM. If the user fails to give the bot a valid email after three failed attempts, the user remains in #guest and is asked to wait for an administrator manually verify them.

# Permissions

Must be given these permissions:
- Manage Roles
- Manage Nicknames
- View Channels
- Send Messages
- Read Message History

The Join Up Bot role should be positioned above any of the roles it will assign or remove. In this case, this will be the admin role.


# Future plans

We will eventually have a visitior role where front-end users will receive one-time codes that grant temporary access to match-specific channels.

# Service deployment notes

The service currently runs on qclub.au under the user discord_bot. The discord_bot has a key added as a deploy_key to the github account.

```bash
discord_bot@qclub.au:~$ git clone git@github.com:pwhipp/discord_join_up_bot.git discord_join_up_bot
discord_bot@qclub.au:~$ cd discord_join_up_bot
discord_bot@qclub.au:~/discord_join_up_bot$ python3.12 -m venv --prompt bot venv
((bot) ) discord_bot@qclub.au:~/discord_join_up_bot$ pip install -r requirements.txt
```

In order to set up the service, so it restarts on reboot:

Copy an appropriate config.yaml. For example:
```bash
(join_up_bot) paul@PWC2:discord_join_up_bot$ rsync config.yaml qclub.au:
```

```bash
paul@qclub.au:~$ sudo mv config.yaml /home/discord_bot/discord_join_up_bot
paul@qclub.au:~$ sudo chown discord_bot:discord_bot /home/discord_bot/discord_join_up_bot/config.yaml
```

```bash
paul@qclub.au:~$ sudo cp /home/discord_bot/discord_join_up_bot/deploy/discord_bot.service /etc/systemd/system/
paul@qclub.au:~$ sudo systemctl enable discord_bot
Created symlink /etc/systemd/system/multi-user.target.wants/discord_bot.service → /etc/systemd/system/discord_bot.service.
```

