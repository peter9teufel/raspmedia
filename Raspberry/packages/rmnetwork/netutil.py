import netifaces

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
                    append = not curIP.startswith('127.') and not curIP.startswith('169.254.')
                if append:
                    ip_list.append(curIP)

    return ip_list

def check_ip6_address(ip6):
    return True
