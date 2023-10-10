#!/usr/bin/env python
from jsonrpclib import Server

def main():
    api = Server("unix:/var/run/command-api.sock")
    logs = api.runCmds(1, ["show logging last 1 minutes"], "text")
    loglines = logs[0]["output"].split('\n')
    interfaceUp = []
    excludedinterfaces = [""]
    portsec = api.runCmds(1, ["show port-security"],
                          "json")[0]["portStatistics"]
    for line in loglines:
        if "LINEPROTO-5-UPDOWN" in line and "changed state to up" in line:
            linesplit = line.split(" ")
            for word in linesplit:
                if ("Ethernet" or "Port-Channel" in word) and (word.strip(",") not in excludedinterfaces) and (word.strip(",") in portsec):
                    interfaceUp.append(word.strip(","))

    if interfaceUp != []:
        staticMac = api.runCmds(
            1, ["show mac address-table static"], "json")[0]["unicastTable"]["tableEntries"]
        staticMacinterface = []
        for mac in staticMac:
            staticMacinterface.append(mac["interface"])
        for interface in interfaceUp:
            if staticMacinterface.count(interface) < portsec[interface]["maxSecureAddr"]:
                dynamicMacinterface = api.runCmds(
                    1, ["show mac address-table dynamic interface " + interface], "json")[0]["unicastTable"]["tableEntries"]
                if dynamicMacinterface != []:
                    for mac in dynamicMacinterface:
                        vlan = mac["vlanId"]
                        macaddr = mac["macAddress"]
                        api.runCmds(1, ["configure", "mac address-table static " +
                                        macaddr + " vlan " + str(vlan) + " interface " + interface])

                    api.runCmds(1, ["write"])

if __name__ == "__main__":
    main()

"""
event-handler sticky
   trigger on-intf Ethernet1-48 operstatus
   delay 5
   action bash python3 /mnt/flash/sticky.py
   repeat interval 5

management api http-commands
   protocol unix-socket
   no shutdown
   !
   vrf MGMT
      no shutdown
"""
