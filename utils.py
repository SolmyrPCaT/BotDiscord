from typing import Dict, Any

LOG_FILE_PATH = "registration_log.txt"


async def write_log_entry(event_name, user_name, action, timestamp):
    try:
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as log_file:
            log_file.write(f"{timestamp.isoformat()} - Event {event_name}: User {user_name} {action}\n")
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
