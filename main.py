import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils import load_registrations, remove_old_events, update_registrations, \
    display_event_users, save_registrations

from datetime import datetime, timedelta

load_dotenv()
DICTABOT_TOKEN = os.getenv("DICTABOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
EVENT_CHECKING_CHANNEL_ID = int(os.getenv("EVENT_CHECKING_CHANNEL_ID"))
JSON_FILE_PATH = "data/registrations.json"


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


@bot.command(name='create_announcement')
async def create_announcement(ctx):
    """
    Commande pour créer un message d'annonce des événements du vendredi et samedi
    de la semaine en cours.
    """
    my_guild = bot.get_guild(GUILD_ID)

    # Obtenir la date actuelle et trouver le vendredi et le samedi de la semaine en cours
    today = datetime.now()
    friday = today + timedelta((4 - today.weekday()) % 7)  # Prochain vendredi
    saturday = today + timedelta((5 - today.weekday()) % 7)  # Prochain samedi

    events_message = ""

    # Récupérer les événements du serveur
    events = await my_guild.fetch_scheduled_events()

    # Filtrer les événements prévus pour vendredi et samedi
    weekend_events = [event for event in events if event.start_time.date() in [friday.date(), saturday.date()]]

    # Si aucun événement n'est trouvé, envoyer un message d'information
    if not weekend_events:
        await ctx.send("Aucun événement prévu pour vendredi et samedi cette semaine.")
        return

    # Construire le message avec les événements filtrés
    for event in weekend_events:
        event_time_unix = int(
            event.start_time.timestamp())
        events_message += f"- Soirée [**{event.name}**]({event.url}) <t:{event_time_unix}:F>\n"

    # Message final avec des informations supplémentaires
    announcement_message = f"@annonce \nCette semaine, on propose les soirées suivantes :\n\n{events_message}\n\n:information_source:  \n\nBonne semaine :wink:"

    # Envoyer le message d'annonce dans le channel de vérification des événements
    test_channel = bot.get_channel(1287444577933983806)
    await test_channel.send(announcement_message)

bot.run(DICTABOT_TOKEN)
