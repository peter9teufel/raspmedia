import netifaces
import platform, subprocess
from packages.rmnetwork.constants import *

def num_connected_interfaces():
    count = 0
    for interface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(interface)
        try:
                inetAddrs = addrs[netifaces.AF_INET]
                for inetA in inetAddrs:
                        if 'broadcast' in inetA and not inetA['broadcast'] == '' and 'addr' in inetA and not inetA['addr'] == '':
                            count += 1
        except:
            pass
    return count

def ip4_addresses():
    ips = _ip_addresses(False)
    return ips

def ip6_addresses():
    ips = _ip_addresses(True)
    return ips

def _ip_addresses(v6):
    ip_list = []

    interfaces = netifaces.interfaces()
    for i in interfaces:
        if i == 'lo':
            continue
        if v6:
            iface = netifaces.ifaddresses(i).get(netifaces.AF_INET6)
        else:
            iface = netifaces.ifaddresses(i).get(netifaces.AF_INET)
        if iface != None:
            for j in iface:
                curIP = j['addr']
                append = False
                if v6:
                    append = check_ip6_address(curIP)
                else:
                    if not curIP.startswith('127.') and not curIP.startswith('169.254'):
                        append = True
                    # append = not curIP.startswith('127.') and not curIP.startswith('169.254.')
                if append:
                    ip_list.append(curIP)

    return ip_list

def check_ip6_address(ip6):
    return True


def wifi_ssids():
    WiFiSSIDs = []

    if platform.system() == 'Windows':
        print "WIFI CHECK on platform Windows:"
        output = subprocess.Popen(["netsh","wlan","show","network"], stdout=subprocess.PIPE).communicate()[0]
        # print output
        lines = output.split('\n')
        curSSID = ''
        keyType = None
        for line in lines:
            words = line.split()
            if len(words) > 3 and words[0] == 'SSID':
                # next SSID found --> add info from previously read network to list of WIFIs
                if len(curSSID) > 0:
                    # print "Appending SSID %s with auth type %s" % (curSSID,keyType)
                    WiFiSSIDs.append({"SSID": curSSID, "AUTHTYPE": keyType})
                # reset variables for ssid and keytype
                curSSID = ''
                keyType = None
                ssid = words[3:]
                for word in ssid:
                    if len(curSSID) > 0:
                        curSSID += " "
                    curSSID += word
            else:
                # look for auth type in other words
                for word in words:
                    if "WPA" in word:
                        keyType = WIFI_AUTH_WPA
                    elif "WEP" in word:
                        keyType = WIFI_AUTH_WEP
            if keyType == None:
                keyType = WIFI_AUTH_NONE
            # WiFiSSIDs.append({"SSID": curSSID, "AUTHTYPE": keyType})
    elif platform.system() == 'Darwin':
        # scan for available WiFi APs
        output = subprocess.Popen(["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-s"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]

        lines = output.split('\n')
        for i in range(1,len(lines)-1):
            # each line represents one available WiFi AP
            line = lines[i]
            apData = line.split()
            curSSID = ''
            ssidDone = False
            keyType = None
            for word in apData:
                if not ssidDone:
                    if word[2] == ':':
                        # BSSID --> ssid done
                        ssidDone = True
                    else:
                        if len(curSSID) > 0:
                            curSSID += " "
                        curSSID += word
                else:
                    # look for auth type in other words
                    if "WPA" in word:
                        keyType = WIFI_AUTH_WPA
                    elif "WEP" in word:
                        keyType = WIFI_AUTH_WEP
            if keyType == None:
                keyType = WIFI_AUTH_NONE

            WiFiSSIDs.append({"SSID": curSSID, "AUTHTYPE": keyType})
    # print WiFiSSIDs
    return WiFiSSIDs
