#!/usr/bin/python3
# Version 4
# Collect Shared Storage Pool data from the HMC and generate googlechart/JavaScript graphing webpage
# In colects whole SSP level and VIOS level stats
import hmc_pcm
import nchart
import time
#HMC and loging details
import sys
if len(sys.argv) != 4:   # four including the program name entry [0]
    print("Usage: %s HMC-hostname HMC-username HMC-password" %(sys.argv[0]))
    sys.exit(1)
hostname=sys.argv[1]
user    =sys.argv[2]
password=sys.argv[3]

print("HMC hostanme=%s User=%s Password=%s"  %( hostname, user, password))

output_html=True
output_csv=False
output_csvold=False

print("-> Logging on to %s as user %s" % (hostname,user))
hmc = hmc_pcm.HMC(hostname, user, password)

print("-> Get Stripped Preferences") # returns XML text
prefstripped = hmc.get_stripped_preferences_ssp()

print("-> Parse Preferences")
ssplist = hmc.parse_prefs_ssp(prefstripped)  # returns a list of dictionaries one per SSP
all_true = True
enabled = []
for ssp in ssplist:
    if ssp['agg'] == 'false' or ssp['mon'] == 'false':
        good = "BAD "
        all_true = False
    else: 
        good = "GOOD"
        enabled.append(ssp)
    print('-> cluster=%-10s pool=%-10s AggregrateEnabled=%5s Monitoring Enabled=%5s =%s' 
        %(ssp['cluster'], ssp['pool'], ssp['agg'], ssp['mon'], good))
if all_true:
    print("-> Skipping Set Preferences as all SSP's are already enabled")
else:
    print("-> Set Preferences - please wait 10+ minutes for stats to appear!")
    prefset = hmc.set_preferences_ssp(prefstripped) # Switches on ALL Aggregatation &  monitoring flags

print("-> Processing SSP")
for count, ssp in enumerate(enabled,start=1):
    print('--> SSP=%d Getting filenames for cluster=%s pool=%s' %(count,ssp['cluster'], ssp['pool']))
    print("---> Requesting %s as monitoring enabled" %(ssp['pool']))
    starttime = time.time()
    JSONfiles = hmc.get_filenames_ssp(ssp['uuid'],ssp['pool']) # returns XML of filename(s)
    endtime = time.time()
    print("---> Received %d file(s) in %.2f seconds" % (len(JSONfiles), endtime - starttime))
    for num,JSONfile in enumerate(JSONfiles,start=1):
        print('---> File=%d Getting stats from %s' %(num,JSONfile['filename']))
        JSONdata = hmc.get_stats(JSONfile['url'],JSONfile['filename'], ssp['pool']) # returns JSON stats
        info = hmc.extract_ssp_info(JSONdata)
        #print(info)
        sspstats = hmc.extract_ssp_totals(JSONdata)
        #print(sspstats[0])
        header, viosstats = hmc.extract_ssp_vios(JSONdata)
        #print(header)
        #print(viosstats[0])
        print("---> Processing JSON data size=%d bytes" % (len(JSONdata)))

        if output_csv:
            filename="SSP-totals-" + info["cluster"] + "-" + info["ssp"] + ".csv"
            f = open(filename,"w")
            f.write("time, size, free, readBytes, writeBytes, readServiceTime-ms, writeServiceTime-ms\n")
            for s in sspstats:
                 buffer="%s, %d,%d, %d,%d, %.3f,%.3f\n" % (s['time'],
                        s['size'],           s['free'], 
                        s['readBytes'],      s['writeBytes'], 
                        s['readServiceTime'],s['writeServiceTime'])
                 f.write(buffer)
            f.close()
            print("Saved SSP Totals comma separated values to %s" % (filename))

            filename="SSP-VIOS-" + info["cluster"] + "-" + info["ssp"] + ".csv"
            f = open(filename,"w")
            f.write("time")
            for viosname in header:
                 f.write("," + viosname)
            f.write("\n")
            for row in viosstats:
                 f.write("%s" % (row["time"]))
                 for readkb in row['readKB']:
                     f.write(",%.3f" % (readkb))
                 for writekb in row['writeKB']:
                     f.write(",%.3f" % (writekb))
                 f.write("\n")
            f.close()
            print("Saved SSP VIOS comma separated values to %s" % (filename))

        if output_csvold:
            filename="SSP_total_io.csv"
            f = open(filename,"a")  # append 
            #f.write("sspname, time, size, free, readBytes, writeBytes, readServiceTime-ms, writeServiceTime-ms\n")
            for s in sspstats:
                 buffer="%s,%s, %d,%d, %d,%d, %.3f,%.3f\n" % (info["ssp"], s['time'],
                        s['size'],           s['free'], 
                        s['readBytes'],      s['writeBytes'], 
                        s['readServiceTime'],s['writeServiceTime'])
                 f.write(buffer)
            f.close()
            print("Saved SSP Totals comma separated values to %s old format" % (filename))

            filename="SSP_vios_io.csv"
            f = open(filename,"a")  # append 
            f.write("%s,Header" % (info["ssp"]))
            for viosname in header:
                 f.write("," + viosname)
            f.write("\n")
            for row in viosstats:
                 f.write("%s" % (row["time"]))
                 for readkb in row['readKB']:
                     f.write(",%.3f" % (readkb))
                 for writekb in row['writeKB']:
                     f.write(",%.3f" % (-writekb))
                 f.write("\n")
            f.close()
            print("Saved SSP VIOS comma separated values to %s old format" % (filename))

        if output_html:                                              # Create .html file that graphs the stats
            filename = "SSP-" + info['ssp'] + ".html"          # Using googlechart
            print("Create %s" %(filename))
            n = nchart.nchart_open()
            n.nchart_ssp(filename, info, sspstats, header, viosstats)
            print("Saved webpage to %s" % (filename))

print("Logging off the HMC")
hmc.logoff()
