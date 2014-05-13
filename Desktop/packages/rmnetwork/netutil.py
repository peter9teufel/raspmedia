import socket

def ip4_addresses():
    ips = _ip_addresses(False)
    return ips

def ip6_addresses():
    ips = _ip_addresses(True)
    return ips

def _ip_addresses(v6):
    ip_list = []
    addrs = socket.getaddrinfo(socket.gethostname(), None)

    for addr in addrs:
        ip = addr[4][0]
        if v6 and _is_ip_v6(ip):
            if not ip in ip_list:
                ip_list.append(ip)
        elif not v6 and _is_ip_v4(ip):
            if not ip in ip_list:
                ip_list.append(ip)

    return ip_list

def _is_ip_v6(ip):
    return ':' in ip

def _is_ip_v4(ip):
    return '.' in ip
