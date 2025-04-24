import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import asyncio
from discord.ui import Button, View
import json

# Load environment variables
load_dotenv()

# Bot configuration
intents = discord.Intents.all()  # Enable all intents

bot = commands.Bot(command_prefix='!', intents=intents)
tree = bot.tree

# Admin role management
MOD_ROLES_FILE = "mod_roles.json"
TICKET_PANEL_FILE = "ticket_panel.json"

def load_mod_roles():
    try:
        with open(MOD_ROLES_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_mod_roles(roles):
    with open(MOD_ROLES_FILE, 'w') as f:
        json.dump(roles, f)

def load_ticket_panel():
    try:
        with open(TICKET_PANEL_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "title": "Support Ticket System",
            "description": "Click the button below to create a new support ticket. A moderator will assist you shortly.",
            "color": "blue"
        }

def save_ticket_panel(panel):
    with open(TICKET_PANEL_FILE, 'w') as f:
        json.dump(panel, f)

def is_admin_or_owner():
    async def predicate(ctx):
        if isinstance(ctx, discord.Interaction):
            if ctx.user.id == ctx.guild.owner_id:
                return True
            user_roles = [role.id for role in ctx.user.roles]
            mod_roles = load_mod_roles()
            return any(role_id in user_roles for role_id in mod_roles)
        if ctx.author.id == ctx.guild.owner_id:
            return True
        user_roles = [role.id for role in ctx.author.roles]
        mod_roles = load_mod_roles()
        return any(role_id in user_roles for role_id in mod_roles)
    return commands.check(predicate)

# Ticket system configuration
TICKET_CATEGORY_NAME = "Tickets"
TICKET_LOGS_CHANNEL = "ticket-logs"
TICKET_PANEL_CHANNEL = "create-ticket"

class TicketButton(Button):
    def __init__(self):
        super().__init__(label="Create Ticket", style=discord.ButtonStyle.green, custom_id="create_ticket")

    async def callback(self, interaction: discord.Interaction):
        try:
            # Get or create ticket category
            category = discord.utils.get(interaction.guild.categories, name=TICKET_CATEGORY_NAME)
            if not category:
                category = await interaction.guild.create_category(TICKET_CATEGORY_NAME)
            
            # Create ticket channel
            ticket_channel = await interaction.guild.create_text_channel(
                f"ticket-{interaction.user.name}",
                category=category,
                topic=f"Ticket created by {interaction.user.name}"
            )
            
            # Set permissions
            await ticket_channel.set_permissions(interaction.guild.default_role, view_channel=False)
            await ticket_channel.set_permissions(interaction.user, view_channel=True, send_messages=True)
            
            # Add moderator permissions
            admin_role = discord.utils.get(interaction.guild.roles, name="Moderator")
            if admin_role:
                await ticket_channel.set_permissions(admin_role, view_channel=True, send_messages=True)
            
            # Create ticket embed
            embed = discord.Embed(
                title="New Ticket Created",
                description=f"Ticket created by {interaction.user.mention}\nPlease describe your issue and a moderator will assist you shortly.",
                color=discord.Color.green()
            )
            
            # Add close button
            close_button = Button(label="Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
            view = View()
            view.add_item(close_button)
            
            # Send initial message
            await ticket_channel.send(embed=embed, view=view)
            await interaction.response.send_message(f"Ticket created! Please check {ticket_channel.mention}", ephemeral=True)
            
            # Log ticket creation
            logs_channel = discord.utils.get(interaction.guild.channels, name=TICKET_LOGS_CHANNEL)
            if logs_channel:
                log_embed = discord.Embed(
                    title="Ticket Created",
                    description=f"Ticket created by {interaction.user.mention}\nChannel: {ticket_channel.mention}",
                    color=discord.Color.blue()
                )
                await logs_channel.send(embed=log_embed)
                
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

class CloseButton(Button):
    def __init__(self):
        super().__init__(label="Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")

    async def callback(self, interaction: discord.Interaction):
        try:
            if not interaction.channel.name.startswith("ticket-"):
                await interaction.response.send_message("This command can only be used in ticket channels!", ephemeral=True)
                return
            
            # Get ticket creator
            ticket_creator = interaction.channel.topic.split("by")[1].strip()
            
            # Create transcript
            messages = []
            async for message in interaction.channel.history(limit=None):
                messages.append(f"{message.author.name}: {message.content}")
            
            transcript = "\n".join(reversed(messages))
            
            # Send transcript to logs
            logs_channel = discord.utils.get(interaction.guild.channels, name=TICKET_LOGS_CHANNEL)
            if logs_channel:
                transcript_embed = discord.Embed(
                    title=f"Ticket Transcript: {interaction.channel.name}",
                    description=f"```{transcript}```",
                    color=discord.Color.red()
                )
                await logs_channel.send(embed=transcript_embed)
            
            # Delete the channel
            await interaction.response.send_message("Closing ticket in 5 seconds...")
            await asyncio.sleep(5)
            await interaction.channel.delete()
            
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

@tree.command(name="setup", description="Setup the moderation system")
@is_admin_or_owner()
async def setup(interaction: discord.Interaction):
    try:
        # Create admin role if it doesn't exist
        admin_role = discord.utils.get(interaction.guild.roles, name="Moderator")
        if not admin_role:
            admin_role = await interaction.guild.create_role(
                name="Moderator",
                color=discord.Color.blue(),
                permissions=discord.Permissions(
                    kick_members=True,
                    ban_members=True,
                    manage_messages=True,
                    manage_roles=True,
                    moderate_members=True
                )
            )
            await interaction.response.send_message(f"Created Moderator role!", ephemeral=True)
        else:
            await interaction.response.send_message(f"Moderator role already exists!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

@tree.command(name="kick", description="Kick a member from the server")
@is_admin_or_owner()
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
@is_admin_or_owner()
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
@is_admin_or_owner()
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
@is_admin_or_owner()
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
@is_admin_or_owner()
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
@is_admin_or_owner()
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
@is_admin_or_owner()
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
@is_admin_or_owner()
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

@tree.command(name="ticketsetup", description="Setup the ticket system")
@is_admin_or_owner()
async def ticketsetup(interaction: discord.Interaction):
    try:
        # Create ticket category if it doesn't exist
        category = discord.utils.get(interaction.guild.categories, name=TICKET_CATEGORY_NAME)
        if not category:
            category = await interaction.guild.create_category(TICKET_CATEGORY_NAME)
        
        # Create ticket panel channel if it doesn't exist
        panel_channel = discord.utils.get(interaction.guild.channels, name=TICKET_PANEL_CHANNEL)
        if not panel_channel:
            panel_channel = await interaction.guild.create_text_channel(
                TICKET_PANEL_CHANNEL,
                category=category
            )
        
        # Create ticket panel embed
        embed = discord.Embed(
            title="Support Ticket System",
            description="Click the button below to create a new support ticket. A moderator will assist you shortly.",
            color=discord.Color.blue()
        )
        
        # Add ticket button
        view = View()
        view.add_item(TicketButton())
        
        # Send panel message
        await panel_channel.send(embed=embed, view=view)
        await interaction.response.send_message("Ticket system has been set up!", ephemeral=True)
        
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

@tree.command(name="addmodrole", description="Add a moderator role by ID")
@is_admin_or_owner()
async def addmodrole(interaction: discord.Interaction, role_id: str):
    try:
        role_id = int(role_id)
        mod_roles = load_mod_roles()
        
        if role_id in mod_roles:
            await interaction.response.send_message("This role is already a moderator role!", ephemeral=True)
            return
        
        # Verify the role exists
        role = interaction.guild.get_role(role_id)
        if not role:
            await interaction.response.send_message("Role not found!", ephemeral=True)
            return
        
        mod_roles.append(role_id)
        save_mod_roles(mod_roles)
        await interaction.response.send_message(f"Added {role.name} as a moderator role!", ephemeral=True)
    except ValueError:
        await interaction.response.send_message("Invalid role ID! Please provide a valid role ID.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

@tree.command(name="removemodrole", description="Remove a moderator role by ID")
@is_admin_or_owner()
async def removemodrole(interaction: discord.Interaction, role_id: str):
    try:
        role_id = int(role_id)
        mod_roles = load_mod_roles()
        
        if role_id not in mod_roles:
            await interaction.response.send_message("This role is not a moderator role!", ephemeral=True)
            return
        
        mod_roles.remove(role_id)
        save_mod_roles(mod_roles)
        
        role = interaction.guild.get_role(role_id)
        role_name = role.name if role else "Unknown Role"
        await interaction.response.send_message(f"Removed {role_name} from moderator roles!", ephemeral=True)
    except ValueError:
        await interaction.response.send_message("Invalid role ID! Please provide a valid role ID.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

@tree.command(name="listmodroles", description="List all moderator roles")
@is_admin_or_owner()
async def listmodroles(interaction: discord.Interaction):
    try:
        mod_roles = load_mod_roles()
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

@tree.command(name="setticketpanel", description="Set the ticket panel embed text (Admin/Owner only)")
@is_admin_or_owner()
async def setticketpanel(interaction: discord.Interaction, title: str, description: str, color: str = "blue"):
    try:
        # Validate color
        valid_colors = ["blue", "red", "green", "yellow", "purple", "orange"]
        if color.lower() not in valid_colors:
            await interaction.response.send_message("Invalid color! Choose from: blue, red, green, yellow, purple, orange", ephemeral=True)
            return
        
        # Save panel settings
        panel = {
            "title": title,
            "description": description,
            "color": color.lower()
        }
        save_ticket_panel(panel)
        
        await interaction.response.send_message("Ticket panel settings updated!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

@tree.command(name="sendticketpanel", description="Send the ticket panel in the current channel (Admin/Owner only)")
@is_admin_or_owner()
async def sendticketpanel(interaction: discord.Interaction):
    try:
        # Load panel settings
        panel = load_ticket_panel()
        
        # Create embed with custom colors
        color_map = {
            "blue": discord.Color.blue(),
            "red": discord.Color.red(),
            "green": discord.Color.green(),
            "yellow": discord.Color.yellow(),
            "purple": discord.Color.purple(),
            "orange": discord.Color.orange()
        }
        
        embed = discord.Embed(
            title=panel["title"],
            description=panel["description"],
            color=color_map.get(panel["color"], discord.Color.blue())
        )
        
        # Add ticket button
        view = View()
        view.add_item(TicketButton())
        
        # Send panel message
        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message("Ticket panel sent!", ephemeral=True)
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

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN')) 