#!/usr/bin/python3
# Version 1
# Set Longterm and Aggregate PCM stats on or off

import hmc_pcm as hmc
import time
import os
import sys

if len(sys.argv) != 6:   # six including the program name entry [0]
    print("Usage: %s HMC-hostname HMC-username HMC-password true|false servername|ALL" %(sys.argv[0]))
    sys.exit(1)
hostname=sys.argv[1]
user    =sys.argv[2]
password=sys.argv[3]
toggle  =sys.argv[4]
mgServer=sys.argv[5]

## Make sure the toggle is true or false
if not (toggle == "true" or toggle == "false"):
    print("%s: Toggle parameter must be true or false" %(sys.argv[0]))
    sys.exit(1) 

print("HMC hostanme=%s User=%s Password=%s On/Off=%s Server(s)=%s"  %( hostname, user, password, toggle, mgServer))

debug=True
debugDir = "./debug"

if not os.path.exists(debugDir):
        os.makedirs(debugDir)

print("-> Logging on to %s as user %s" % (hostname,user))
hmc = hmc.HMC(hostname, user, password)
print("-> Get server details")
serverDetails = hmc.get_server_details_pcm()
print("-> Get current preferences") # returns XML text
prefstripped = hmc.get_stripped_preferences_pcm()

## If debug is enabled save a copy of the current prefernces
if debug:
    print("-> Saving current repferences to directory: %s" %debugDir)
    hmc.save_to_file("server_perferences.xml",prefstripped)

print("-> Parse current Preferences")
serverlist = hmc.parse_prefs_pcm(prefstripped)  # returns a list of dictionaries one per Server
perflist = []
all_true = True

for num,server in enumerate(serverlist):
    ## Process all managed servers for this HMC
    if mgServer == "ALL":
        print("-> Processing server=%-16s"%server['name'])
        print("-> Set LTM and AGG preferences to: %-5s" %toggle)
        hmc.set_ltm_flag(server['name'], toggle)
        hmc.set_preferences_pcm()
    ## Process just the individual managed server specified in parameter 5    
    elif not mgServer == "ALL":
        if server['name'] == mgServer:
            print("-> Processing server=%-16s"%server['name'])
            print("-> Set LTM and AGG preferences to: %-5s" %toggle)
            hmc.set_ltm_flag(server['name'], toggle)
            hmc.set_preferences_pcm()
        else:
            print("-> Ignoring server=%-16s"%server['name'])

print("Logging off the HMC")
hmc.logoff()
