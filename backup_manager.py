#!/usr/bin/env python3

import argparse
import re
import os
import time
import subprocess
import signal

def backupManager():
    args = ParseArgs()
    if args.command == "create":
        createBackupSchedule(args.schedule)
    elif args.command == "list":
        listBackupSchedules()
        # print("Listing backup schedules in backup_schedules.txt...")
    elif args.command == "delete":
        deleteBackupSchedule(args.index)
        # print(f"Deleting backup schedule at index {args.index}...")
    elif args.command == "start":
        startProcess()
        # print("Starting backup service...")
    elif args.command == "stop":
        # print("Stopping backup service...")
        stopProcess()
    elif args.command == "backups":
        # print("Listing backup files in ./backups...")
        ListBackupExist()
    else:
        print("No command provided. Use -h for help.")


def ParseArgs():
    parser  = argparse.ArgumentParser(add_help=False)
    superParser = parser.add_subparsers(dest="command")
    createParser = superParser.add_parser("create", help="add a new backup schedule to backup_schedules.txt")
    createParser.add_argument("schedule", help="the backup schedule to add to backup_schedules.txt")
    superParser.add_parser("list", help="list all backup schedules in backup_schedules.txt")
    deleteParser = superParser.add_parser("delete", help="Delete the backup schedule at the given index (starting at 0) from backup_schedules.txt")
    deleteParser.add_argument("index", help="the index of the backup schedule to delete from backup_schedules.txt", type=int)
    superParser.add_parser("start", help="Run backup_service.py in the background")
    superParser.add_parser("stop", help="Kill the backup_service.py process")
    superParser.add_parser("backups", help="List the backup files in ./backups")
    args = parser.parse_args()
    return args

def createBackupSchedule(schedule):
    now = time.time()
    timestr = time.strftime("%d/%m/%Y %H:%M", time.localtime(now))
    content = ""
    if checkScheduleFormat(schedule):
        content = f"[{timestr}] New schedule added: {schedule}"
        WriteInFile("backup_schedules.txt", schedule)
    else:
        content = f"[{timestr}] Error: malformed schedule: {schedule}"
    writeInLogFile(content)
    

def checkScheduleFormat(schedule):
    return re.match(r"[a-zA-Z0-9]+;[0-9]+:[0-9]+;[a-zA-Z0-9]+", schedule)

def WriteInFile(filename, content):
    if os.path.exists(filename):
        with open(filename, "a") as f:
            f.write(content + "\n")
    else:
        with open(filename, "w") as f:
            f.write(content + "\n")

def writeInLogFile(content):
    os.makedirs("logs", exist_ok=True)
    WriteInFile("logs/backup_manager.log", content)

def listBackupSchedules():
    now = time.time()
    timestr = time.strftime("%d/%m/%Y %H:%M", time.localtime(now))
    try:
        with open("backup_schedules.txt", "r") as f:
            schedules = f.readlines()
        for i, schedule in enumerate(schedules):
            print(f"{i}: {schedule.strip()}")
        writeInLogFile(f"[{timestr}] Show schedules list")
    except FileNotFoundError:
        writeInLogFile(f"[{timestr}] Error: can't find backup_schedules.txt")

def deleteBackupSchedule(index):
    now = time.time()
    timestr = time.strftime("%d/%m/%Y %H:%M", time.localtime(now))
    content = ''
    try:
        with open("backup_schedules.txt", "r") as f:
            schedules = f.readlines()
        if len(schedules[index].strip()) != 0:
            del schedules[index]
        else:
            content = f"[{timestr}] Error: can't find schedule at index {index}"
            return
        with open("backup_schedules.txt", "w") as f:
            f.writelines(schedules)
        content = f"[{timestr}] Schedule at index {index} deleted"
    except FileNotFoundError:
        content = f"[{timestr}] Error: can't find backup_schedules.txt"
    except IndexError:
        content = f"[{timestr}] Error: can't find schedule at index {index}"
    finally:
        writeInLogFile(content)
         
def startProcess():
    now = time.time()
    timestr = time.strftime("%d/%m/%Y %H:%M", time.localtime(now))
    content = ''
    checkProcess = subprocess.Popen(
        ["pgrep", "-f", "backup_service.py"],
        stdout=subprocess.PIPE,
        text=True
    )
    msg, _ = checkProcess.communicate()
    if msg.strip():
        content = "Error: backup_service already running"
    else:
        process = subprocess.Popen(['./backup_service.py'], start_new_session=True)
        content = "backup_service started"
        with open("pid.txt", 'w') as f:
            f.write(str(process.pid))
    writeInLogFile(f"[{timestr}] {content}")

def stopProcess():
    now = time.time()
    timestr = time.strftime("%d/%m/%Y %H:%M", time.localtime(now))
    content = ""
    try:
        with open('pid.txt', 'r') as f:
            processID = int(f.read())
        os.kill(processID, 0)
        os.kill(processID, signal.SIGTERM)
        os.remove("pid.txt")
        content = "backup_service stopped"
    except (FileNotFoundError, ValueError, OSError, PermissionError):
        content = "Error: can't stop backup_service"
    finally:
        writeInLogFile(f"[{timestr}] {content}")

def ListBackupExist():
    now = time.time()
    timestr = time.strftime("%d/%m/%Y %H:%M", time.localtime(now))
    content = ""
    if not os.path.exists("./backups"):
        content = "Error: can't find backups directory"
    else:
        entrys = os.listdir("./backups")
        for entry in entrys:
            print(entry)
        content = "Show backups list"
    writeInLogFile(f"[{timestr}] {content}")


if __name__ == "__main__":
    backupManager()