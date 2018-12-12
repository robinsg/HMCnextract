#!/usr/bin/python3
# Version 4
import hmc_pcm
import nchart

import sys
if len(sys.argv) != 4:   # four including the program name entry [0]
    print("Usage: %s HMC-hostname HMC-username HMC-password" %(sys.argv[0]))
    sys.exit(1)
hostname=sys.argv[1]
user    =sys.argv[2]
password=sys.argv[3]

print("HMC hostanme=%s User=%s Password=%s"  %( hostname, user, password))

output_html=True
output_csv=True
output_csv_v1=False

print("-> Logging on to %s as user %s" % (hostname,user))
hmc = hmc_pcm.HMC(hostname, user, password)                      # Log on to the HMC
#hmc.set_debug(True)
serverlist = hmc.get_server_details_pcm()                        # Get list of attached Managed Servers dictionary

for count, server in enumerate(serverlist,start=1):              # Loop through the Servers
    if server['capable'] == 'false':
        print("-->Server %d %s not capable of supplying energy stats"%(count,server['name']))
        continue
    if server['energy'] == 'false':
        print("-->Server %d %s is energy stats capable but not enabled"%(count,server['name']))
        continue
    print("-->Server %d %s collecting Energy stats"%(count,server['name']))
    JSONdata = hmc.get_energy(server['atomid'],server['name'])   # get the stats for this Server
    if JSONdata == None:
        continue
    info = hmc.extract_energy_info(JSONdata)                     # converts JSON into summary info
    print("-->Summary:")
    print(info)
    headline,stats = hmc.extract_energy_stats(JSONdata)          # converts JSON into CSV column-name
                                                                 # watts+temp stats as a list of dictionaries
    if output_html:                                              # Create .html file that graphs the stats
        filename = "Energy-" + server['name'] + ".html"          # Using googlechart
        print("Create %s" %(filename))
        n = nchart.nchart_open()
        n.nchart_energy(filename, info, stats)
        print("Saved webpage to %s" % (filename))

    if output_csv:                                               # Create comma separated values file
        filename = "Energy-" + server['name'] + ".csv"
        f = open(filename,"w")
        f.write("%s\n" %(headline))
        for s in stats:
            f.write("%s, %.1f, %.1f,%.1f,%.1f,%.1f, %.1f,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f, %.1f\n" %
                 (s['time'],s['watts'],s['mb0'],s['mb1'],s['mb2'],s['mb3'],
                  s['cpu0'],s['cpu1'],s['cpu2'],s['cpu3'],s['cpu4'],s['cpu5'],s['cpu6'],s['cpu7'],
                  s['inlet']) )
        f.close()
        print("Saved comma separated values to %s" % (filename))

    if output_csv_v1:                                            # Create comma separated values file,old version
        filename = "energy.csv"
        f = open(filename,"a")
        f.write("%s\n" %(headline))
        for s in stats:
            date1 =s['time']
            # pick out the year, month(starting with zero), day and hour, mins, seconds
            date2 = date1[0:4] + "-" +  str(int(date1[5:7]) -1) + "-" + date1[8:10] + "-" + date1[11:13] + "-" + date1[14:16] + "-" + date1[17:]
            if info['mtm']== '8408-E8E':    # E850 has all stats
                f.write("%s,%s,%s,%s,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f\n" %
                 (info['server'], info['mtm'], info['serial'],
                  date2,s['watts'],s['mb0'],s['mb1'],s['mb2'],s['mb3'],
                  s['cpu0'],s['cpu1'],s['cpu2'],s['cpu3'],s['cpu4'],s['cpu5'],s['cpu6'],s['cpu7'],
                  s['inlet']) )
            else:    # Others have less stats
                f.write("%s,%s,%s,%s,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f\n" %
                 (info['server'], info['mtm'], info['serial'],
                  date2,s['watts'],s['mb0'],s['mb1'],s['mb2'],
                  s['cpu0'],s['cpu1'],s['cpu2'],s['cpu3'],
                  s['inlet']) )

        f.close()
        print("Saved comma separated values to %s in older tool format" % (filename))
