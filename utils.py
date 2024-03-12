LOG_FILE_PATH = "registration_log.txt"


async def write_log_entry(event_id, user_id, action, timestamp):
    with open(LOG_FILE_PATH, "a", encoding="utf-8") as log_file:
        log_file.write(f"{timestamp.isoformat()} - Event {event_id}: User {user_id} {action}\n")
