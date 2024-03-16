import os

from datetime import datetime

import discord
from discord.ext import commands

from dotenv import load_dotenv

import json

from utils import write_log_entry, rank

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
    await check_event_registrations()


async def check_event_registrations():
    def serialize_datetime(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError("Type not serializable")

    current_time = datetime.now()

    try:
        with open(JSON_FILE_PATH, "r") as file:
            registrations = json.load(file)
    except FileNotFoundError:
        registrations = {}
        print(f"Le fichier {JSON_FILE_PATH} n'a pas été trouvé.")
    except json.JSONDecodeError as e:
        registrations = {}
        print(f"Erreur lors de la lecture du fichier JSON : {e}")

    my_guild = bot.get_guild(GUILD_ID)

    if my_guild:
        scheduled_events = sorted(my_guild.scheduled_events, key=lambda x: x.start_time)
        for event in scheduled_events:
            current_users_ids = set([str(user.id) async for user in event.users()])
            event_id = str(event.id)
            print(f"Event {event_id}")
            if event_id in registrations:
                prev_user_ids = set([user for user in registrations[event_id].keys()])
            else:
                prev_user_ids = set()
            users_in = current_users_ids.difference(prev_user_ids)
            users_out = prev_user_ids.difference(current_users_ids)
            if users_out:
                for user_id in users_out:
                    registrations[event_id].pop(user_id, None)
                    event_name = event.name if event else f"Événement inconnu (ID: {event_id})"
                    member = my_guild.get_member(int(user_id))
                    user_name = member.name if member else f"Utilisateur inconnu (ID: {user_id})"
                    await write_log_entry(event_name, user_name, "se désinscrit", current_time)
            elif users_in:
                if event_id not in registrations:
                    registrations[event_id] = {}
                for user_id in users_in:
                    if user_id not in registrations[event_id]:
                        registrations[event_id][user_id] = current_time
                        event_name = event.name if event else f"Événement inconnu (ID: {event_id})"
                        member = my_guild.get_member(int(user_id))
                        user_name = member.name if member else f"Utilisateur inconnu (ID: {user_id})"
                        await write_log_entry(event_name, user_name, "s'inscrit", current_time)
            else:
                print(f"{event.name} : No Changes")

    with open(JSON_FILE_PATH, "w") as file:
        json.dump(registrations, file, indent=4, default=serialize_datetime)


async def list_rank_event_users(ctx, event_id):
    my_guild = bot.get_guild(GUILD_ID)
    print("rank déclenché")
    try:
        with open(JSON_FILE_PATH, "r") as file:
            registrations = json.load(file)
    except FileNotFoundError:
        registrations = {}

    for event_id_str, users_dict in registrations.items():
        if event_id_str == str(event_id):
            event = my_guild.get_scheduled_event(int(event_id_str))
            event_name = event.name if event else f"Événement inconnu (ID: {event_id_str})"

            sorted_users = sorted(users_dict.items(),
                                  key=lambda x: datetime.fromisoformat(x[1]))  # Trier par date d'inscription
            ranks = rank(dict(sorted_users))

            message = f"## Ordre d'inscription : {event_name} :\n \n"

            for user_id, registration_time in sorted_users:
                rank_str = str(ranks[user_id])
                user_id = int(user_id)
                # Convertir la chaîne en objet datetime si nécessaire
                if not isinstance(registration_time, datetime):
                    registration_time = datetime.fromisoformat(registration_time)

                # Obtenez l'objet membre
                member = my_guild.get_member(user_id)
                # Utilisez le pseudo si le membre est trouvé, sinon utilisez l'ID
                user_name = member.name if member else f"Utilisateur inconnu (ID: {user_id})"
                formatted_registration_time = registration_time.strftime("%d/%m/%Y %H:%M")
                message += f" {rank_str} -- {user_name} inscrit le {formatted_registration_time}\n"

            # Envoyer le message dans le canal de votre choix
            message += "--------------------------------------------------------------------------------"
            await ctx.send(message)


@bot.command(name='event_users')
async def event_users(ctx, event_id: int):
    """
    Affiche la liste des inscrits pour un événement spécifié.
    Utilisation : $event_users <event_id>
    """
    print("rank déclenché")
    await list_rank_event_users(ctx, event_id)


bot.run(DICTABOT_TOKEN)
