LOG_FILE_PATH = "registration_log.txt"


async def write_log_entry(event_name, user_name, action, timestamp):
    try:
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as log_file:
            log_file.write(f"{timestamp.isoformat()} - Event {event_name}: User {user_name} {action}\n")
    except IOError as e:
        print(f"Erreur lors de l'écriture dans le fichier de journal : {e}")
