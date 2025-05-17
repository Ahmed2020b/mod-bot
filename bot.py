import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
from database import Database

# Load environment variables
load_dotenv()

# Bot configuration
intents = discord.Intents.all()  # Enable all intents
intents.message_content = True  # Enable message content intent

# Custom prefix
bot = commands.Bot(command_prefix='-', intents=intents)
tree = bot.tree

# Initialize database
db = Database()

# Role ID for رصد command permission (replace with your role ID)
RADD_ROLE_ID = 1367905739183624344  # Replace this with your role ID

def has_manage_server():
    async def predicate(ctx):
        if isinstance(ctx, discord.Interaction):
            return ctx.user.guild_permissions.manage_guild
        return ctx.author.guild_permissions.manage_guild
    return commands.check(predicate)

def has_radd_role():
    async def predicate(ctx):
        return any(role.id == RADD_ROLE_ID for role in ctx.author.roles)
    return commands.check(predicate)

# Custom command for رصد
@bot.command(name="رصد")
@has_radd_role()
async def radd(ctx, member: discord.Member, amount: int):
    try:
        # DM message template (you can edit this message)
        dm_message = f"""
        ⚠️ **تنبيه** ⚠️
        تم رصدك من قبل {ctx.author.mention}
        المبلغ: {amount}
        الرجاء دفع الى البنك المركزي
        """
        
        # Send DM to the mentioned user
        await member.send(dm_message)
        await ctx.send(f"تم إرسال التنبيه إلى {member.mention}")
        
    except discord.Forbidden:
        await ctx.send(f"لا يمكنني إرسال رسالة خاصة إلى {member.mention}")
    except Exception as e:
        await ctx.send(f"حدث خطأ: {str(e)}")

# Slash Commands
@tree.command(name="kick", description="Kick a member from the server")
@has_manage_server()
async def kick_slash(interaction: discord.Interaction, member: discord.Member, reason: str = None):
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
@has_manage_server()
async def ban_slash(interaction: discord.Interaction, member: discord.Member, reason: str = None):
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
@has_manage_server()
async def unban_slash(interaction: discord.Interaction, member: str):
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
@has_manage_server()
async def clear_slash(interaction: discord.Interaction, amount: int):
    try:
        if amount <= 0 or amount > 100:
            await interaction.response.send_message("Please specify a number between 1 and 100", ephemeral=True)
            return
        
        await interaction.channel.purge(limit=amount + 1)
        await interaction.response.send_message(f'Cleared {amount} messages!', ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

# Prefix Commands
@bot.command(name="kick")
@commands.has_permissions(manage_guild=True)
async def kick_prefix(ctx, member: discord.Member, *, reason: str = None):
    try:
        if reason is None:
            reason = "No reason provided"
        
        if member.top_role >= ctx.author.top_role:
            await ctx.send("You cannot kick someone with a higher or equal role!")
            return
        
        await member.kick(reason=reason)
        await ctx.send(f'Kicked {member.mention} for: {reason}')
    except discord.Forbidden:
        await ctx.send("I don't have permission to kick members!")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

@bot.command(name="ban")
@commands.has_permissions(manage_guild=True)
async def ban_prefix(ctx, member: discord.Member, *, reason: str = None):
    try:
        if reason is None:
            reason = "No reason provided"
        
        if member.top_role >= ctx.author.top_role:
            await ctx.send("You cannot ban someone with a higher or equal role!")
            return
        
        await member.ban(reason=reason)
        await ctx.send(f'Banned {member.mention} for: {reason}')
    except discord.Forbidden:
        await ctx.send("I don't have permission to ban members!")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

@bot.command(name="unban")
@commands.has_permissions(manage_guild=True)
async def unban_prefix(ctx, *, member: str):
    try:
        banned_users = [entry async for entry in ctx.guild.bans()]
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user
            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f'Unbanned {user.mention}')
                return
        
        await ctx.send(f"Could not find banned user {member}")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

@bot.command(name="clear")
@commands.has_permissions(manage_guild=True)
async def clear_prefix(ctx, amount: int):
    try:
        if amount <= 0 or amount > 100:
            await ctx.send("Please specify a number between 1 and 100")
            return
        
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f'Cleared {amount} messages!', delete_after=5)
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

@tree.command(name="addmod", description="Add a moderator role to a member")
@has_manage_server()
async def addmod(interaction: discord.Interaction, member: discord.Member):
    try:
        admin_role = discord.utils.get(interaction.guild.roles, name="Moderator")
        if not admin_role:
            await interaction.response.send_message("Moderator role not found! Please run /setup first.", ephemeral=True)
            return
        
        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message("You cannot add moderator role to someone with a higher or equal role!", ephemeral=True)
            return
        
        await member.add_roles(admin_role)
        await interaction.response.send_message(f'Added Moderator role to {member.mention}')
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

@tree.command(name="removemod", description="Remove moderator role from a member")
@has_manage_server()
async def removemod(interaction: discord.Interaction, member: discord.Member):
    try:
        admin_role = discord.utils.get(interaction.guild.roles, name="Moderator")
        if not admin_role:
            await interaction.response.send_message("Moderator role not found! Please run /setup first.", ephemeral=True)
            return
        
        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message("You cannot remove moderator role from someone with a higher or equal role!", ephemeral=True)
            return
        
        await member.remove_roles(admin_role)
        await interaction.response.send_message(f'Removed Moderator role from {member.mention}')
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

@tree.command(name="addmodrole", description="Add a moderator role by ID")
@has_manage_server()
async def addmodrole(interaction: discord.Interaction, role_id: str):
    try:
        role_id = int(role_id)
        mod_roles = db.get_mod_roles()
        
        if role_id in mod_roles:
            await interaction.response.send_message("This role is already a moderator role!", ephemeral=True)
            return
        
        # Verify the role exists
        role = interaction.guild.get_role(role_id)
        if not role:
            await interaction.response.send_message("Role not found!", ephemeral=True)
            return
        
        db.add_mod_role(role_id)
        await interaction.response.send_message(f"Added {role.name} as a moderator role!", ephemeral=True)
    except ValueError:
        await interaction.response.send_message("Invalid role ID! Please provide a valid role ID.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

@tree.command(name="removemodrole", description="Remove a moderator role by ID")
@has_manage_server()
async def removemodrole(interaction: discord.Interaction, role_id: str):
    try:
        role_id = int(role_id)
        mod_roles = db.get_mod_roles()
        
        if role_id not in mod_roles:
            await interaction.response.send_message("This role is not a moderator role!", ephemeral=True)
            return
        
        db.remove_mod_role(role_id)
        
        role = interaction.guild.get_role(role_id)
        role_name = role.name if role else "Unknown Role"
        await interaction.response.send_message(f"Removed {role_name} from moderator roles!", ephemeral=True)
    except ValueError:
        await interaction.response.send_message("Invalid role ID! Please provide a valid role ID.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

@tree.command(name="listmodroles", description="List all moderator roles")
@has_manage_server()
async def listmodroles(interaction: discord.Interaction):
    try:
        mod_roles = db.get_mod_roles()
        if not mod_roles:
            await interaction.response.send_message("No moderator roles have been set up yet!", ephemeral=True)
            return
        
        roles_info = []
        for role_id in mod_roles:
            role = interaction.guild.get_role(role_id)
            if role:
                roles_info.append(f"• {role.name} (ID: {role_id})")
            else:
                roles_info.append(f"• Unknown Role (ID: {role_id})")
        
        embed = discord.Embed(
            title="Moderator Roles",
            description="\n".join(roles_info),
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

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

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please provide all required arguments!")
    elif isinstance(error, commands.CheckFailure):
        if ctx.command.name == "رصد":
            await ctx.send("You don't have the required role to use this command!")
        else:
            await ctx.send("You don't have permission to use this command!")

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN')) 