import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils import load_registrations, remove_old_events, update_registrations, \
    display_event_users, save_registrations

load_dotenv()
DICTABOT_TOKEN = os.getenv("DICTABOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
EVENT_CHECKING_CHANNEL_ID = int(os.getenv("EVENT_CHECKING_CHANNEL_ID"))
JSON_FILE_PATH = "registrations.json"


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guild_scheduled_events = True
bot = commands.Bot(command_prefix='$', intents=intents)


@bot.event
async def on_ready():
    print("Le bot est prêt")
    my_guild = bot.get_guild(GUILD_ID)
    registrations = load_registrations(JSON_FILE_PATH)
    registrations = remove_old_events(registrations)
    await update_registrations(my_guild, registrations)
    save_registrations(registrations, JSON_FILE_PATH)


@bot.command(name='event_users')
async def event_users(ctx, event_id: int):
    """
    Affiche la liste des inscrits pour un événement spécifié.
    Utilisation : $event_users <event_id>
    """
    my_guild = bot.get_guild(GUILD_ID)
    registrations = load_registrations(JSON_FILE_PATH)
    message = display_event_users(registrations, my_guild, event_id)
    await ctx.send(message)


bot.run(DICTABOT_TOKEN)
