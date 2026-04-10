#!/usr/bin/env python3
import time
from datetime import datetime
from backup_manager import WriteInFile
import os
import tarfile

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
        readSchedule()
        time.sleep(45)

def readSchedule():
    new_shchedules = []
    try:
        with open("backup_schedules.txt", "r") as f:
            schedules = f.readlines()
        for schedule in schedules:
            data = extractData(schedule)
            now = datetime.now()
            t = time.time()
            hour = data["hour"]
            minute = data["minute"]
            timestr = time.strftime("%d/%m/%Y %H:%M", time.localtime(t))
            if hour == now.hour and minute == now.minute :
                path = data["path"]
                back = data["backup_name"]
                try:
                    createTars(f"{back}.tar", path, timestr)
                    writeInLogFile(f"[{timestr}] Backup done for {path} in backups/{back}.tar")

                except (FileNotFoundError, tarfile.TarError):
                    writeInLogFile(f"{timestr} Error: we can't create {back} source not found {path}")
            elif not is_time_passed(f"{hour}:{minute}"):
                new_shchedules.append(schedule)

        with open("backup_schedules.txt", "w") as f:
            f.writelines(new_shchedules)
                   
    except:
        writeInLogFile("Error We can't create backup")
        

def extractData(schedule):
    sli = schedule.split(";")
    if len(sli) != 3:
        return None
    path_to_save = sli[0].strip()
    we9t = sli[1].strip()
    backup_name = sli[2].strip()
    time_sli = we9t.split(":")
    if len(time_sli) != 2:
        return None
    hour = time_sli[0].strip()
    minute = time_sli[1].strip()
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

def createTars(target, source, timestr):
    try:
        os.makedirs("backups", exist_ok=True)
        with tarfile.open(f"backups/{target}", "w") as tar:
            tar.add(source)
        writeInLogFile(f"[{timestr}] Backup done for {source} in backups/{target}")
    except (FileNotFoundError, tarfile.TarError) as e:
        os.remove(f"backups/{target}")
        raise e
    

def is_time_passed(schedule_time):
    now = datetime.now()

    target = datetime.strptime(schedule_time, "%H:%M")
    target = target.replace(
        year=now.year,
        month=now.month,
        day=now.day
    )
    return now >= target

backup_service()
    
