# Discord Moderation Bot

A Discord moderation bot with slash commands and admin role management.

## Features

- Slash commands support
- Admin role management system
- Kick members
- Ban/Unban members
- Clear messages
- Mute/Unmute members
- Permission-based command access

## Local Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the same directory and add your Discord bot token:
```
DISCORD_TOKEN=your_bot_token_here
```

3. Run the bot:
```bash
python bot.py
```

## Railway Deployment

1. Fork this repository to your GitHub account
2. Go to [Railway](https://railway.app/) and create a new project
3. Connect your GitHub repository
4. Add the following environment variables in Railway:
   - `DISCORD_TOKEN`: Your Discord bot token
5. Deploy the project

## Commands

### Setup Commands
- `/setup` - Set up the moderation system (creates Moderator role)

### Moderation Commands
- `/kick @user [reason]` - Kick a member from the server
- `/ban @user [reason]` - Ban a member from the server
- `/unban username#discriminator` - Unban a member
- `/clear [number]` - Clear a specified number of messages
- `/mute @user [reason]` - Mute a member
- `/unmute @user` - Unmute a member

### Admin Management Commands
- `/addmod @user` - Add moderator role to a member
- `/removemod @user` - Remove moderator role from a member

## Bot Permissions

Make sure to give your bot the following permissions when inviting it to your server:
- Manage Messages
- Kick Members
- Ban Members
- Manage Roles
- Read Messages/View Channels
- Send Messages
- Read Message History
- Use Slash Commands

## Admin Role System

The bot uses a "Moderator" role for admin management. To use the moderation commands:
1. Run `/setup` to create the Moderator role
2. Use `/addmod` to give moderator permissions to trusted members
3. Only members with the Moderator role can use moderation commands

## Note

This bot requires Python 3.8 or higher to run. #   m o d - b o t  
 