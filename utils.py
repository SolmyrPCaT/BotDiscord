import json
from datetime import datetime, timezone
from typing import Dict, Any

LOG_FILE_PATH = "registration_log.txt"


async def write_log_entry(guild, event, user_id, action, timestamp):
    event_id = str(event.id)
    event_name = event.name if event else f"Événement inconnu (ID: {event_id})"
    member = guild.get_member(int(user_id))
    user_name = member.name if member else f"Utilisateur inconnu (ID: {user_id})"

    try:
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as log_file:
            log_file.write(f"{timestamp.isoformat()} - Event {event_name}: {user_name} {action}\n")
    except IOError as e:
        print(f"Erreur lors de l'écriture dans le fichier de journal : {e}")


def rank(dictionary: Dict[str, Any]) -> Dict[str, int]:
    sorted_items = sorted(dictionary.items(), key=lambda x: x[1])
    ranks = {}
    current_rank = 1
    for i, (key, value) in enumerate(sorted_items):
        if i > 0 and value != sorted_items[i - 1][1]:
            current_rank = i + 1
        ranks[key] = current_rank
    return ranks


def load_registrations(path):
    try:
        with open(path, "r") as file:
            registrations = json.load(file)
    except FileNotFoundError:
        registrations = {}
        print(f"Le fichier {path} n'a pas été trouvé.")
    except json.JSONDecodeError as e:
        registrations = {}
        print(f"Erreur lors de la lecture du fichier JSON : {e}")

    return registrations


def serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError("Type not serializable")


def remove_old_events(registrations):
    current_time = datetime.now(timezone.utc)
    events_to_delete = []
    for event, info in registrations.items():
        event_date = datetime.fromisoformat(info['date'])
        if event_date < current_time:
            events_to_delete.append(event)

    for event in events_to_delete:
        print(f"Suppresion de l'event {registrations[event]['name']}")
        del registrations[event]

    return registrations


async def update_registrations(guild, registrations):
    current_time = datetime.now(timezone.utc)
    scheduled_events = sorted(guild.scheduled_events, key=lambda x: x.start_time)

    for event in scheduled_events:
        event_id = str(event.id)
        current_users_ids = set([str(user.id) async for user in event.users()])
        if event_id in registrations:
            prev_user_ids = set([user for user in registrations[event_id]['users'].keys()])
        else:
            prev_user_ids = set()
        users_in = current_users_ids.difference(prev_user_ids)
        users_out = prev_user_ids.difference(current_users_ids)

        if users_out:
            for user_id in users_out:
                registrations[event_id]['users'].pop(user_id, None)
                await write_log_entry(guild, event, user_id, "se désincrit", current_time)

        elif users_in:
            if event_id not in registrations:
                registrations[event_id] = {
                    'name': event.name,
                    'date': event.start_time,
                    'users': {}
                }
            for user_id in users_in:
                if user_id not in registrations[event_id]['users']:
                    registrations[event_id]['users'][user_id] = current_time
                    await write_log_entry(guild, event, user_id, "s'inscrit", current_time)
        else:
            print(f"{event.name} : No Changes")

    return registrations


def display_event_users(registrations, my_guild, event_id):
    message = ''
    for event_id_str, info in registrations.items():
        users_dict = info['users']
        if event_id_str == str(event_id):
            event = my_guild.get_scheduled_event(int(event_id_str))
            event_name = event.name if event else f"Événement inconnu (ID: {event_id_str})"
            sorted_users = sorted(                        # Tri par date d'inscription
                users_dict.items(),
                key=lambda x: datetime.fromisoformat(x[1])
            )
            ranks = rank(dict(sorted_users))
            message = f"## Ordre d'inscription : {event_name} :\n \n"
            for user_id, registration_time in sorted_users:
                rank_str = str(ranks[user_id])
                user_id = int(user_id)
                if not isinstance(registration_time, datetime):
                    registration_time = datetime.fromisoformat(registration_time)
                member = my_guild.get_member(user_id)
                user_name = member.name if member else f"Utilisateur inconnu (ID: {user_id})"
                formatted_registration_time = registration_time.strftime("%d/%m/%Y %H:%M")
                message += f" {rank_str} -- {user_name} inscrit le {formatted_registration_time}\n"
            message += "--------------------------------------------------------------------------------"
    return message


def save_registrations(registrations, path):
    with open(path, "w") as file:
        json.dump(registrations, file, indent=4, default=serialize_datetime)
