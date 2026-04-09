#!/usr/bin/env python3
import time
from datetime import datetime
from backup_manager import WriteInFile
import os

#The schedule format is "path_to_save;HH:MM;backup_name"
#///////////////////////////////////////////////////////////////////////////////////
# python3 ./backup_manager.py create "test;16:07;backup_test"
# python3 ./backup_manager.py create "test1;16:07;personal_data"
# python3 ./backup_manager.py create "test2;16:07;office_docs"
#///////////////////////////////////////////////////////////////////////////////////
# personal_data.tar
# office_docs.tar
# backup_test.tar
def backup_service():
    while True:
        now = datetime.now()
        readSchedule(now)
        
        time.sleep(45)


def readSchedule(now):
    try:
        with open("backup_schedules.txt", "r") as f:
            schedules = f.readlines()
        for schedule in schedules :
            data = extractData(schedule)
        if data["hour"] == now.hour and data["minute"] == now.minute :
            writeInLogFile("the date are matching")
    except FileNotFoundError:
        writeInLogFile("Error We can't create backup")

def extractData(schedule):
    sli = schedule.split(";")
    if len(sli) != 3:
        return None
    path_to_save = sli[0]
    we9t = sli[1]
    backup_name = sli[2]
    time_sli = we9t.split(":")
    if len(time_sli) != 2:
        return None
    hour = time_sli[0]
    minute = time_sli[1]
    return {
        "path": path_to_save,
        "time": we9t,
        "hour": int(hour),
        "minute": int(minute),
        "backup_name": backup_name
    }

def writeInLogFile(content):
    os.makedirs("logs", exist_ok=True)
    WriteInFile("logs/backup_service.log", content)

backup_service()
    
