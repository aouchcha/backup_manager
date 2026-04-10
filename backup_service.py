#!/usr/bin/env python3
import os
import tarfile
import time
from datetime import datetime

from backup_manager import get_logger

LOGGER = get_logger("backup_service", "backup_service.log")
SCHEDULES_FILE = "backup_schedules.txt"
BACKUPS_DIR = "backups"


def backup_service():
    while True:
        process_schedules(datetime.now())
        time.sleep(45)


def process_schedules(now):
    try:
        with open(SCHEDULES_FILE, "r") as file:
            raw_schedules = file.readlines()
    except FileNotFoundError:
        LOGGER.error("Can't process backups because %s is missing", SCHEDULES_FILE)
        return

    remaining_schedules = []
    current_minutes = now.hour * 60 + now.minute

    for raw_schedule in raw_schedules:
        schedule = extract_data(raw_schedule)
        if schedule is None:
            LOGGER.error("Skipping malformed schedule: %s", raw_schedule.strip())
            continue

        scheduled_minutes = schedule["hour"] * 60 + schedule["minute"]
        if scheduled_minutes > current_minutes:
            remaining_schedules.append(raw_schedule if raw_schedule.endswith("\n") else f"{raw_schedule}\n")
            continue

        if scheduled_minutes == current_minutes:
            create_backup(schedule)
        else:
            LOGGER.info("Removing expired schedule: %s", raw_schedule.strip())

    write_schedules(remaining_schedules)


def extract_data(schedule):
    parts = schedule.strip().split(";")
    if len(parts) != 3:
        return None

    source_path, scheduled_time, backup_name = parts
    time_parts = scheduled_time.split(":")
    if len(time_parts) != 2:
        return None

    try:
        hour = int(time_parts[0])
        minute = int(time_parts[1])
    except ValueError:
        return None

    if not 0 <= hour <= 23 or not 0 <= minute <= 59:
        return None

    return {
        "path": source_path,
        "time": scheduled_time,
        "hour": hour,
        "minute": minute,
        "backup_name": backup_name,
    }


def create_backup(schedule):
    source_path = schedule["path"]
    backup_name = schedule["backup_name"]

    if not os.path.exists(source_path):
        LOGGER.error("Backup source does not exist: %s", source_path)
        return

    os.makedirs(BACKUPS_DIR, exist_ok=True)
    archive_path = os.path.join(BACKUPS_DIR, f"{backup_name}.tar")
    archive_member = os.path.basename(os.path.abspath(source_path))

    try:
        with tarfile.open(archive_path, "w") as archive:
            archive.add(source_path, arcname=archive_member)
        LOGGER.info("Backup created: %s from %s", archive_path, source_path)
    except (OSError, tarfile.TarError) as error:
        LOGGER.error("Failed to create backup for %s: %s", source_path, error)


def write_schedules(schedules):
    with open(SCHEDULES_FILE, "w") as file:
        file.writelines(schedules)


if __name__ == "__main__":
    backup_service()
