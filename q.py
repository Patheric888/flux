import discord
from discord.ext import commands
import os

# --- CONFIGURATION ---
STAFF_ROLE_ID = 1411414376925233273  # 🔹 Replace with your Staff role ID
TICKET_CATEGORY_ID = 1438258856923893802  # 🔹 Optional: category ID for all tickets (int)

# --- SETUP BOT ---
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ------------------------------------------------------------
# Ticket Select Menu
# ------------------------------------------------------------
class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Support", description="Get help or report an issue", emoji="🛠️"),
            discord.SelectOption(label="Purchase", description="Buy a product or service", emoji="💳"),
            discord.SelectOption(label="Media", description="Media or partnership inquiries", emoji="🎬"),
            discord.SelectOption(label="Resell", description="Information for resellers", emoji="💼"),
        ]
        super().__init__(
            placeholder="Select a ticket category...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user
        category = self.values[0].lower()
        channel_name = f"{category}-{user.name}".replace(" ", "-").lower()

        # Prevent duplicate tickets
        for ch in guild.text_channels:
            if ch.name == channel_name:
                await interaction.response.send_message(
                    f"You already have an open ticket: {ch.mention}",
                    ephemeral=True
                )
                return

        # Permissions
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }

        staff_role = guild.get_role(STAFF_ROLE_ID)
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        # Create the ticket channel
        if TICKET_CATEGORY_ID:
            category_obj = bot.get_channel(TICKET_CATEGORY_ID)
            if category_obj is None:
                await interaction.response.send_message(
                    "⚠️ Ticket category not found. Please check the category ID.",
                    ephemeral=True
                )
                return
            channel = await category_obj.create_text_channel(channel_name, overwrites=overwrites)
        else:
            channel = await guild.create_text_channel(channel_name, overwrites=overwrites)

        embed = discord.Embed(
            title=f"🎫 Flux Ticket - {category.capitalize()}",
            description=f"Hello {user.mention}! Please describe your issue or request below.\n\nA member of **Flux Team** will assist you soon.",
            color=0x00FFFF
        )

        await channel.send(embed=embed)
        await interaction.response.send_message(f"✅ Ticket created: {channel.mention}", ephemeral=True)


# ------------------------------------------------------------
# Ticket View (dropdown)
# ------------------------------------------------------------
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())


# ------------------------------------------------------------
# Command to send the panel
# ------------------------------------------------------------
@bot.command()
@commands.has_permissions(administrator=True)
async def ticketpanel(ctx):
    embed = discord.Embed(
        title="🎟️ Flux Ticket System",
        description=(
            "Create a ticket below for **questions, support, purchases, and more.**\n\n"
            "**How to open a ticket:**\n"
            "Select a category from the dropdown menu below based on your needs.\n\n"
            "**Guidelines:**\n"
            "• Only one ticket at a time\n"
            "• Be patient and respectful\n"
            "• Provide detailed information\n"
            "• We do **NOT** assist users coming from resellers"
        ),
        color=0x00FFFF
    )
    embed.set_footer(text="Flux Tickets © 2025")

    await ctx.send(embed=embed, view=TicketView())


# ------------------------------------------------------------
# READY EVENT
# ------------------------------------------------------------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} | Ready to go!")
    try:
        synced = await bot.tree.sync()
        print(f"🔁 Synced {len(synced)} app commands.")
    except Exception as e:
        print(f"⚠️ Command sync failed: {e}")


# ------------------------------------------------------------
# RUN BOT (Railway compatible)
# ------------------------------------------------------------
TOKEN = os.getenv("MTQzODExMTE4ODk3NzMxOTk0Ng.GzTllP.uUkwjror_99rlJOZ7m5fam9l5iplX57nOm9ejM")

if TOKEN is None:
    print("❌ BOT_TOKEN not found. Please add it in Railway → Settings → Variables.")
else:
    bot.run(TOKEN)
