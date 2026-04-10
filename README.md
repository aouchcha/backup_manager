# Backup Manager

## Description

Backup Manager is an automated backup system built in Python.  
It runs in the background, follows a schedule, and logs every action automatically.

The system is made of two scripts that work together:
- `backup_manager.py` — the CLI tool you use to manage schedules and control the service
- `backup_service.py` — the background service that performs the backups automatically

---

## Project Structure

```
backup-manager/
├── backup_manager.py        # CLI script for managing schedules and service
├── backup_service.py        # Background service that performs scheduled backups
├── logs/                    # Directory for log files (created at runtime)
│   ├── backup_manager.log   # Logs from backup_manager.py
│   └── backup_service.log   # Logs from backup_service.py
├── backups/                 # Directory for backup .tar files (created at runtime)
├── backup_schedules.txt     # Schedule file (created at runtime)
└── README.md                # Project documentation
```

---

## Requirements

- Python 3.x
- Linux / macOS (uses `pgrep -f "process_name"` for process management)
- No external libraries needed (only Python standard library)

---

## Schedule Format

Each schedule follows this format:

```
path_to_save;HH:MM;backup_name
```

| Field | Description | Example |
|---|---|---|
| `path_to_save` | Path of the folder to backup | `documents` |
| `HH:MM` | Time to perform the backup | `16:07` |
| `backup_name` | Name of the output `.tar` file | `my_backup` |

**Example:**
```
documents;16:07;my_backup
```

---

## Usage

### Create a new schedule
```bash
python3 backup_manager.py create "path_to_save;HH:MM;backup_name"
```
**Example:**
```bash
python3 backup_manager.py create "documents;16:07;my_backup"
```

---

### List all schedules
```bash
python3 backup_manager.py list
```
**Output:**
```
0: documents;16:07;my_backup
1: photos;18:00;photos_backup
```

---

### Delete a schedule
```bash
python3 backup_manager.py delete [index]
```
**Example:**
```bash
python3 backup_manager.py delete 0
```

---

### Start the backup service
```bash
python3 backup_manager.py start
```
The service runs in the background and checks schedules every 45 seconds.

---

### Stop the backup service
```bash
python3 backup_manager.py stop
```

---

### List all backups
```bash
python3 backup_manager.py backups
```
**Output:**
```
my_backup.tar
photos_backup.tar
```

---

## How It Works

```
You (terminal)
      │
      ▼
backup_manager.py
      │
      ├── writes to ──► backup_schedules.txt ◄── read by ──► backup_service.py
      │                                                             │
      ├── starts/stops ───────────────────────────────────────────►│ (runs in background)
      │                                                             │
      └── reads ◄─────── ./backups/ ◄──── creates .tar files ──────┘
                          ./logs/
```

1. You create schedules with `backup_manager.py create`
2. You start the service with `backup_manager.py start`
3. `backup_service.py` runs in the background and checks every 45 seconds
4. When the time matches a schedule → it creates a `.tar` backup in `./backups/`
5. The schedule is removed from the file after the backup is done
6. Everything is logged in `./logs/`

---

## Logs

All actions and errors are logged automatically.

| File | Description |
|---|---|
| `logs/backup_manager.log` | Logs from all CLI commands |
| `logs/backup_service.log` | Logs from the background service |

**Log format:**
```
[dd/mm/yyyy HH:MM] message
```

**Example:**
```
[10/04/2026 16:07] New schedule added: documents;16:07;my_backup
[10/04/2026 16:07] backup_service started
[10/04/2026 16:07] backup_service stopped
[10/04/2026 16:07] Backup done for documents in backups/my_backup.tar
```

---

## Error Handling

The system handles all errors without crashing and logs them properly.

| Situation | Log message |
|---|---|
| Malformed schedule | `Error: malformed schedule: ...` |
| Schedule file not found | `Error: can't find backup_schedules.txt` |
| Index not found | `Error: can't find schedule at index X` |
| Service already running | `Error: backup_service already running` |
| Service not running | `Error: can't stop backup_service` |
| Backups directory not found | `Error: can't find backups directory` |
| Source folder not found | `Backup source does not exist: source` |
| Unknown command | `No valid command provided. Use -h for help.` |

---

## Example

```bash
# Create test folders
mkdir test test1 test2

# Create schedules
python3 backup_manager.py create "test;16:07;backup_test"
python3 backup_manager.py create "test1;16:07;personal_data"
python3 backup_manager.py create "test2;16:07;office_docs"

# List schedules
python3 backup_manager.py list

# Start the service
python3 backup_manager.py start
sleep 5

# Stop the service
python3 backup_manager.py stop

# See the backups created
python3 backup_manager.py backups

# Check the logs
cat ./logs/backup_manager.log
cat ./logs/backup_service.log
```

---