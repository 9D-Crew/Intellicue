# Imports
import paramiko
import configparser
import threading
import schedule
import datetime
import time as time_py

# End Imports
print("Intellicue\n(C) 2025 9D Crew")

# Config Loading
config = configparser.ConfigParser(); config.read('config.ini') # Load Config File
global ip; global port; global username; global password; global lot8s; global ldl; global run_time # Global Everything
# Load Config Into Python Variables
ip = config['SSH']['IP']
port = config['SSH']['PORT']; port = int(port)
username = config['SSH']['USERNAME']; password = config['SSH']['PASSWORD']
lot8s = config['FLAVOR']['LOT8S']; ldl = config['FLAVOR']['LDL']
run_time = config['FLAVOR']['RUN_TIME']; run_time = int(run_time)
print("Config Loaded Successfully")
print("Using LOT8s Flavor", lot8s, "And LDL Flavor", ldl)

# i1 Connection
print("Connecting to i1..")
global ssh_client, shell; ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(ip, port=port, username=username, password=password, look_for_keys=False, allow_agent=False)
shell = ssh_client.invoke_shell()

def password_man(): # No clue what this does, but it's in i1-encoder so wth
    global shell
    while True:
        output = shell.recv(1024).decode()
        if "Password:" in output:
            shell.send("i1\n")
threading.Thread(target=password_man, daemon=True).start()
shell.send("su -l dgadmin\n") # Switch user to dgadmin

def cmd(command):
    global shell
    print(f">{command}")
    shell.send(command + "\n")

print("i1 Connected.")
cmd("runomni /twc/util/toggleNationalLDL.pyc 0") # In case LDL is loaded, which it shouldn't be.

# List of all LOT8s Flavors, with their respective runtimes.
lot8s_times = {
    'S': 67,
    'M' : 200,
    'K' : 140,
    'E' : 100,
    'D' : 100,
    'L' : 195
}
# Function for calculating time until LOT8s.
def lot8s_time_calc(run_time: int) -> int:
    time_slots = {
        1: [18, 48],                     # modern
        2: [28, 58],                     # future
        3: [8, 18, 28, 38, 48, 58],      # classic
        4: [0, 30]                       # half-hour
    }

    now = datetime.datetime.now()
    current_minute = now.minute
    current_second = now.second
    current_microsecond = now.microsecond
    next_minutes = [m for m in time_slots[run_time] if m > current_minute or 
                   (m == current_minute and (current_second > 0 or current_microsecond > 0))]
    if next_minutes:
        next_minute = next_minutes[0]
        next_hour = now.hour
    else:
        next_minute = time_slots[run_time][0]
        next_hour = (now.hour + 1) % 24

    next_run = now.replace(hour=next_hour, minute=next_minute, second=0, microsecond=0)
    if next_run <= now: 
        # This should never EVER happen.
        print("WHAT THE FUCK")
        raise Exception("congradulations you won the lottery")

    delta = next_run - now
    return int(delta.total_seconds() * 1000 + delta.microseconds / 1000)


while True:
    print("Starting LDL")
    cmd(f"runomni /twc/util/toggleNationalLDL.pyc {ldl}") # Start LDL
    time = lot8s_time_calc(run_time) # Calculate how much time until next LOT8s
    print("next cue in", time) # inform user
    time_py.sleep(time / 1000) # wait for next lot8s
    print("cueing")
    cmd(f"runomni /twc/util/toggleNationalLDL.pyc 0") # Stop LDL
    cmd(f"runomni /twc/util/load.pyc local {lot8s}") # Load LOT8s
    time_py.sleep(0.1) # race condition fix?
    cmd(f"runomni /twc/util/run.pyc local") # Run LOT8s
    time = lot8s_times.get(lot8s)
    time_py.sleep(time)