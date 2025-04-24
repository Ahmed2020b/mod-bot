import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration
intents = discord.Intents.all()  # Enable all intents

bot = commands.Bot(command_prefix='!', intents=intents)
tree = bot.tree

# Admin role management
ADMIN_ROLE_NAME = "Moderator"

def is_admin():
    async def predicate(ctx):
        if isinstance(ctx, discord.Interaction):
            return any(role.name == ADMIN_ROLE_NAME for role in ctx.user.roles)
        return any(role.name == ADMIN_ROLE_NAME for role in ctx.author.roles)
    return commands.check(predicate)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    # Set status to DND and activity to "NW NIGHT WISCONSIN"
    await bot.change_presence(
        status=discord.Status.dnd,
        activity=discord.Game(name="NW NIGHT WISCONSIN")
    )
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@tree.command(name="setup", description="Setup the moderation system")
@is_admin()
async def setup(interaction: discord.Interaction):
    try:
        # Create admin role if it doesn't exist
        admin_role = discord.utils.get(interaction.guild.roles, name=ADMIN_ROLE_NAME)
        if not admin_role:
            admin_role = await interaction.guild.create_role(
                name=ADMIN_ROLE_NAME,
                color=discord.Color.blue(),
                permissions=discord.Permissions(
                    kick_members=True,
                    ban_members=True,
                    manage_messages=True,
                    manage_roles=True,
                    moderate_members=True
                )
            )
            await interaction.response.send_message(f"Created {ADMIN_ROLE_NAME} role!", ephemeral=True)
        else:
            await interaction.response.send_message(f"{ADMIN_ROLE_NAME} role already exists!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

@tree.command(name="kick", description="Kick a member from the server")
@is_admin()
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    try:
        if reason is None:
            reason = "No reason provided"
        
        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message("You cannot kick someone with a higher or equal role!", ephemeral=True)
            return
        
        await member.kick(reason=reason)
        await interaction.response.send_message(f'Kicked {member.mention} for: {reason}')
    except discord.Forbidden:
        await interaction.response.send_message("I don't have permission to kick members!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

@tree.command(name="ban", description="Ban a member from the server")
@is_admin()
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    try:
        if reason is None:
            reason = "No reason provided"
        
        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message("You cannot ban someone with a higher or equal role!", ephemeral=True)
            return
        
        await member.ban(reason=reason)
        await interaction.response.send_message(f'Banned {member.mention} for: {reason}')
    except discord.Forbidden:
        await interaction.response.send_message("I don't have permission to ban members!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

@tree.command(name="unban", description="Unban a member from the server")
@is_admin()
async def unban(interaction: discord.Interaction, member: str):
    try:
        banned_users = [entry async for entry in interaction.guild.bans()]
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user
            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await interaction.guild.unban(user)
                await interaction.response.send_message(f'Unbanned {user.mention}')
                return
        
        await interaction.response.send_message(f"Could not find banned user {member}", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

@tree.command(name="clear", description="Clear a specified number of messages")
@is_admin()
async def clear(interaction: discord.Interaction, amount: int):
    try:
        if amount <= 0 or amount > 100:
            await interaction.response.send_message("Please specify a number between 1 and 100", ephemeral=True)
            return
        
        await interaction.channel.purge(limit=amount + 1)
        await interaction.response.send_message(f'Cleared {amount} messages!', ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

@tree.command(name="mute", description="Mute a member")
@is_admin()
async def mute(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    try:
        if reason is None:
            reason = "No reason provided"
        
        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message("You cannot mute someone with a higher or equal role!", ephemeral=True)
            return
        
        muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
        if not muted_role:
            muted_role = await interaction.guild.create_role(name="Muted")
            for channel in interaction.guild.channels:
                await channel.set_permissions(muted_role, speak=False, send_messages=False)
        
        await member.add_roles(muted_role)
        await interaction.response.send_message(f'Muted {member.mention} for: {reason}')
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

@tree.command(name="unmute", description="Unmute a member")
@is_admin()
async def unmute(interaction: discord.Interaction, member: discord.Member):
    try:
        muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
        if muted_role in member.roles:
            await member.remove_roles(muted_role)
            await interaction.response.send_message(f'Unmuted {member.mention}')
        else:
            await interaction.response.send_message(f'{member.mention} is not muted!', ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

@tree.command(name="addmod", description="Add a moderator role to a member")
@is_admin()
async def addmod(interaction: discord.Interaction, member: discord.Member):
    try:
        admin_role = discord.utils.get(interaction.guild.roles, name=ADMIN_ROLE_NAME)
        if not admin_role:
            await interaction.response.send_message("Moderator role not found! Please run /setup first.", ephemeral=True)
            return
        
        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message("You cannot add moderator role to someone with a higher or equal role!", ephemeral=True)
            return
        
        await member.add_roles(admin_role)
        await interaction.response.send_message(f'Added {ADMIN_ROLE_NAME} role to {member.mention}')
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

@tree.command(name="removemod", description="Remove moderator role from a member")
@is_admin()
async def removemod(interaction: discord.Interaction, member: discord.Member):
    try:
        admin_role = discord.utils.get(interaction.guild.roles, name=ADMIN_ROLE_NAME)
        if not admin_role:
            await interaction.response.send_message("Moderator role not found! Please run /setup first.", ephemeral=True)
            return
        
        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message("You cannot remove moderator role from someone with a higher or equal role!", ephemeral=True)
            return
        
        await member.remove_roles(admin_role)
        await interaction.response.send_message(f'Removed {ADMIN_ROLE_NAME} role from {member.mention}')
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please provide all required arguments!")

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN')) 