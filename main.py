# Imports
import paramiko
import configparser
import threading
from typing import Dict, List
import schedule
import datetime
import time as time_py

# End Imports
intellilogo = r"""
 ___       _       _ _ _                 
|_ _|_ __ | |_ ___| | (_) ___ _   _  ___ 
 | || '_ \| __/ _ \ | | |/ __| | | |/ _ \
 | || | | | ||  __/ | | | (__| |_| |  __/
|___|_| |_|\__\___|_|_|_|\___|\__,_|\___|
"""
print(intellilogo)
print("(C) 2025 9D Crew")

# Config Loading
print("Loading config..")
config = configparser.ConfigParser(); config.read('config.ini')
ssh_config = config['SSH']; flavor_config = config['FLAVOR']
ip = ssh_config.get('IP'); port = ssh_config.getint('PORT')
username = ssh_config.get('USERNAME'); password = ssh_config.get('PASSWORD')
lot8s = flavor_config.get('LOT8S'); ldl = flavor_config.get('LDL')
run_time = flavor_config.getint('RUN_TIME')
print("Config Loaded Successfully.")
print(f"Using LOT8s Flavor: {lot8s} and LDL Flavor: {ldl}")

# i1 Connection
print("Connecting to i1..")
global ssh_client, shell, password; ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(ip, port=port, username=username, password=password, look_for_keys=False, allow_agent=False)
shell = ssh_client.invoke_shell()

def password_man(): # this is in i1-encoder, so its probably important..
    global shell
    while True:
        output = shell.recv(1024).decode()
        if "Password:" in output:
            shell.send(f"{password}\n")

threading.Thread(target=password_man, daemon=True).start()
shell.send("su -l dgadmin\n") # switch to dgadmin

def cmd(command):
    global shell
    print(f">{command}")
    shell.send(command + "\n")

print("i1 Connected.")
shell.send("runomni /twc/util/toggleNationalLDL.pyc 0\n") # disable ldl because it's probably still running from a previous instance

# Local on the 8s Flavor Length Lookup Table
lot8s_times = {
    'D': 100,
    'E': 100,
    'K': 140,
    'L': 195,
    'M': 200,
    'N': 162,
    'O': 145,
    'S': 67
}

# Function for calculating time until LOT8s.
def lot8s_time_calc(run_time: int) -> int:
    time_slots: Dict[int, List[int]] = {
        1: [18, 48],                    # modern
        2: [28, 58],                    # future
        3: [8, 18, 28, 38, 48, 58],     # classic
        4: [0, 30]                      # half-hour
    }

    now = datetime.datetime.now()
    current_time = now.replace(microsecond=0)

    for minute in sorted(time_slots[run_time]):
        candidate = now.replace(minute=minute, second=0, microsecond=0)
        if candidate >= current_time:
            next_run = candidate
            break
    else:
        next_run = now.replace(
            hour=now.hour + 1,
            minute=min(time_slots[run_time]),
            second=0,
            microsecond=0
        )
    
    delta = next_run - now
    return max(0, int(delta.total_seconds() * 1000))

print("Setup done, Starting loop.")

while True: # Main Loop
    cmd(f"runomni /twc/util/toggleNationalLDL.pyc {ldl}") # Start LDL
    time = lot8s_time_calc(run_time); time_py.sleep(time / 1000) # Wait for next LOT8s Cue
    cmd(f"runomni /twc/util/toggleNationalLDL.pyc 0") # Stop LDL
    cmd(f"runomni /twc/util/load.pyc local {lot8s}") # Load LOT8s
    time_py.sleep(0.1) # race condition fix
    cmd(f"runomni /twc/util/run.pyc local") # Run LOT8s

    time = lot8s_times.get(lot8s); time_py.sleep(time) # Wait for LOT8s to finish
