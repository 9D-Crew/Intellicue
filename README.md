# IntelliCue

**Automated LOT8s and LDL Scheduler for IntelliStar 1 Systems**
(C) 2025 9D Crew

```
 ___       _       _ _ _                 
|_ _|_ __ | |_ ___| | (_) ___ _   _  ___ 
 | || '_ \| __/ _ \ | | |/ __| | | |/ _ \
 | || | | | ||  __/ | | | (__| |_| |  __/
|___|_| |_|\__\___|_|_|_|\___|\__,_|\___|
```

---

## Overview

**IntelliCue** is a Python-based automation tool for managing Local on the 8s (LOT8s) and LDL playback on legacy IntelliStar 1 (i1) systems. It connects over SSH, manages session authentication, and uses a timing system to run playouts at the correct broadcast intervals.

This script is useful for restoring or simulating the automated behavior of IntelliStar 1 in hobbyist or archival broadcast environments.

---

## Features

* Connects to i1 via SSH (using `paramiko`)
* Automatically responds to system password prompts
* Enables/disables LDL on schedule
* Cues LOT8s at the correct intervals using flavor and time mode
* Includes predefined LOT8s duration mappings
* Configurable via external INI file

---

## Requirements

* Python 3.6 or newer
* `paramiko`
* `schedule`

### Installation

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

**requirements.txt**

```
paramiko
schedule
```

---

## Configuration

Create a `config.ini` in the same directory as the script. Use the following template:

```ini
[FLAVOR]
LOT8S = M
; The Following LOT8s Flavors are Supported
; S, M, K, E, D, and L.
; See LOT8s_Times.txt

LDL = 1
; 1 to enable LDL
; 0 to disable LDL

RUN_TIME = 1
; 1 for modern (:18 and :48)
; 2 for future (:28 and :58)
; 3 for classic (:08 :18 :28 :38 :48 :58)
; 4 for half-hour (:00 and :30)

[SSH]
IP = 192.168.0.227
PORT = 22
USERNAME = root
PASSWORD = i1
```

---

## Usage

To run IntelliCue:

```bash
python3 intellicue.py
```

The script will:

1. Connect to your i1 system over SSH
2. Switch to `dgadmin` and stop any currently running LDL session
3. Calculate when the next LOT8s segment is scheduled to begin
4. Toggle LDL and run the specified LOT8s flavor at the appropriate time
5. Repeat the process in an infinite loop

---

## LOT8s Flavors

| Code | Duration (seconds) |
| ---- | ------------------ |
| S    | 67                 |
| M    | 200                |
| K    | 140                |
| E    | 100                |
| D    | 100                |
| L    | 195                |

---

## Notes

* Be cautious: the script directly controls live system playback.
* A background thread monitors for password prompts and auto-replies.
* LDL is explicitly disabled before each LOT8s cycle to avoid conflicts.
* Intended for use with real IntelliStar 1s

---

Let me know if you’d like a `LOT8s_Times.txt` reference table or want to include screenshots or output examples.
