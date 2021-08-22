#!/usr/bin/env python
import time
from jsonrpclib import Server

def main():
    api = Server("unix:/var/run/command-api.sock")    
    logs = api.runCmds(1, ["show logging last 1 minutes"],"text" )
    loglines = logs[0]["output"].split('\n')
    interfaceUp= []
    excludedinterfaces = [""]
    for line in loglines:
        if "LINEPROTO-5-UPDOWN" in line and "changed state to up" in line:
            linesplit = line.split(" ")
            for word in linesplit:
                if ("Ethernet" in word) and (word not in excludedinterfaces):
                    interfaceUp.append(word.strip(","))
    if interfaceUp != []:
        staticMac = api.runCmds(1, ["show mac address-table static"],"json" )[0]["unicastTable"]["tableEntries"]
        staticMacinterface = []
        for mac in staticMac:
            staticMacinterface.append(mac["interface"])
        for interface in interfaceUp:
            if interface not in staticMacinterface:
                showMacinterface = api.runCmds(1, ["show mac address-table interface " + interface],"json" )[0]["unicastTable"]["tableEntries"]
                if showMacinterface != []:
                    macTableinterface = showMacinterface[0]
                    vlan = macTableinterface["vlanId"]
                    mac = macTableinterface["macAddress"]
                    api.runCmds(1, ["configure", "mac address-table static " + mac + " vlan " + str(vlan) + " interface " + interface])
if __name__ == "__main__":
    main()

"""
event-handler sticky
   trigger on-intf Ethernet1-48 operstatus
   delay 5
   action bash python /mnt/flash/sticky.py

management api http-commands
   protocol unix-socket
   no shutdown
   !
   vrf MGMT
      no shutdown
"""
