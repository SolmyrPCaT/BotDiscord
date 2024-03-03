import os
import time
from pprint import pprint
import asyncio
from datetime import datetime

import discord
from discord.ext import commands
from dotenv import load_dotenv

from typing import Dict, Any


load_dotenv()

DICTABOT_TOKEN = os.getenv("DICTABOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
EVENT_CHECKING_CHANNEL_ID = int(os.getenv("EVENT_CHECKING_CHANNEL_ID"))

intents = discord.Intents.default()
intents.members = True
intents.guild_scheduled_events = True

bot = commands.Bot(command_prefix='$', intents=intents)


@bot.event
async def on_ready():
    print("Le bot est prêt")
    await check_event_registrations()

registrations = []

async def check_event_registrations():

    def rank(dictionary: Dict[str, Any]) -> Dict[str, int]:
        sorted_items = sorted(dictionary.items(), key=lambda x: x[1])
        ranks = {}
        current_rank = 1
        for i, (key, value) in enumerate(sorted_items):
            if i > 0 and value != sorted_items[i - 1][1]:
                current_rank = i + 1
            ranks[key] = current_rank
        return ranks

    while True:

        guild = bot.get_guild(GUILD_ID)  # GUILD_ID par l'ID de votre serveur
        current_time = datetime.now()
        registrations = dict() # Pour un event, on a l'identifiant en clé et en valeur un dictionnaire avec l'identifiant de l'user en clé et la date d'inscription en valeur

        if guild:
            scheduled_events = sorted(guild.scheduled_events, key=lambda x: x.start_time)
            for event in scheduled_events:
                current_users_ids = set([user.id async for user in event.users()])
                if event.id in registrations:
                    prev_user_ids = set([user for user in registrations[event.id].keys()])
                else:
                    prev_user_ids = set()

                users_in = current_users_ids.difference(prev_user_ids)
                users_out = prev_user_ids.difference(current_users_ids)
                # pprint(users_in)
                # pprint(users_out)
                if users_out:
                    # Les enlever de registrations
                    for user in users_out:
                        registrations[event.id].pop(user, None)
                elif users_in:
                    if event.id not in registrations:
                        registrations[event.id] = {}
                    for user in users_in:
                        if user not in registrations[event.id]:
                            registrations[event.id][user] = current_time
                else:
                    print(f"{event.name} : No Changes")

        # print("Enregistrements :\n", registrations)

        for event_id, users_dict in registrations.items():
            event = guild.get_scheduled_event(event_id)
            event_name = event.name if event else f"Événement inconnu (ID: {event_id})"

            sorted_users = sorted(users_dict.items(), key=lambda x: x[1])  # Trier par date d'inscription
            ranks = rank(dict(sorted_users))

            message = f"## Ordre d'inscription : {event_name} :\n \n"

            for user_id, registration_time in sorted_users:
                rank_str = str(ranks[user_id])
                # Obtenez l'objet membre
                member = guild.get_member(user_id)
                # Utilisez le pseudo si le membre est trouvé, sinon utilisez l'ID
                user_name = member.name if member else f"Utilisateur inconnu (ID: {user_id})"
                formatted_registration_time = registration_time.strftime("%d/%m/%Y %H:%M")
                message += f"{rank_str} {user_name} inscrit le {formatted_registration_time}\n"
            # Envoyer le message dans le canal de votre choix
            message += "--------------------------------------------------------------------------------"
            channel = bot.get_channel(EVENT_CHECKING_CHANNEL_ID)  # Remplacez YOUR_CHANNEL_ID par l'ID de votre canal
            await channel.send(message)

        await asyncio.sleep(180)  # Attendre 3 minutes (180 secondes)

        # await asyncio.sleep(180)  # Attendre 1 heure (3600 secondes)


bot.run(DICTABOT_TOKEN)

# general = guild.get_channel(1000122289209217179)
# await general.send("I'm Back")
# await general.send(
#     "https://tenor.com/view/%C3%B3culos-escuro-exterminador-terminator-arnold-schwarzenegger-gif-14440790")