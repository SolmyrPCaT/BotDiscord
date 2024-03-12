import os

from datetime import datetime

import discord
from discord.ext import commands

from dotenv import load_dotenv

import json


load_dotenv()

DICTABOT_TOKEN = os.getenv("DICTABOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
EVENT_CHECKING_CHANNEL_ID = int(os.getenv("EVENT_CHECKING_CHANNEL_ID"))
JSON_FILE_PATH = "registrations.json"


intents = discord.Intents.default()
intents.members = True
intents.guild_scheduled_events = True

bot = commands.Bot(command_prefix='$', intents=intents)
my_guild = bot.get_guild(GUILD_ID)  # GUILD_ID par l'ID de votre serveur


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
                # Les enlever de registrations
                for user in users_out:
                    registrations[event_id].pop(user, None)
            elif users_in:
                if event_id not in registrations:
                    registrations[event_id] = {}
                for user in users_in:
                    if user not in registrations[event_id]:
                        registrations[event_id][user] = current_time
            else:
                print(f"{event.name} : No Changes")

    with open(JSON_FILE_PATH, "w") as file:
        json.dump(registrations, file, indent=4, default=serialize_datetime)


bot.run(DICTABOT_TOKEN)

