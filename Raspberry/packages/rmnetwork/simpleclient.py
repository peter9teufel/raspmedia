import sys, threading, time
import socket, select
import udpbroadcastlistener

def appendBytes(data, append, LE=False):
    if LE:
        for b in reversed(append):
            data.append(int(b))
    else:
        for b in append:
            data.append(int(b))
    return data

def appendInt(data, num, LE=True):
    sizeBytes = [hex(num >> i & 0xff) for i in (24,16,8,0)]
    sizeBytes = [int(num >> i & 0xff) for i in (24,16,8,0)]
    return appendBytes(data, sizeBytes, LE)

def appendShort(data, num, LE=True):
    sizeBytes = [int(num >> i & 0xff) for i in (8,0)]
    return appendBytes(data, sizeBytes, LE)

def appendString(data, str, sizeLE=True):
    strBytes = bytearray(str, 'utf8')
    data = appendInt(data, len(strBytes), sizeLE)
    return appendBytes(data, strBytes)


def appendArg(data, type, arg):
    if type == '-f':
        global flag
        flag = int(arg)
    elif type == '-w':
        appendShort(data, int(arg))
    elif type == '-s':
        appendString(data, arg)
    elif type == '-i':
        appendInt(data, int(arg,0))


def getMessage(flag, args=None):
    # append all arguments given as cmd args to usgData
    usgData = bytearray()
    if args:
        # print args
        for i in range(0,len(args)):
            arg = args[i]
            if arg.startswith('-'):
                if i < len(args) - 1:
                    appendArg(usgData, arg, args[i+1])

    # combine msg size and usgData in final message to send in data
    data = bytearray()
    size = 6
    if usgData:
        size += len(usgData)
    appendInt(data, size)
    appendShort(data, flag)
    if usgData:
        appendBytes(data, usgData)
    return data

def main():
    global sock
    data = None
    flag = -1

    if len(sys.argv) > 3:
        flag = int(sys.argv[2])
        args = sys.argv[3:]
        data = getMessage(flag, args)
    elif len(sys.argv) == 3:
        flag = int(sys.argv[2])
        data = getMessage(flag)

    host = '<broadcast>'
    port = 60005


    # if valid message data and flag present --> send it
    if data and not flag == -1:
        print "Creating socket..."
        # SOCK_DGRAM is the socket type to use for UDP sockets
        print "Starting broadcast response listening thread..."
        rcv_thread = threading.Thread(target=udpbroadcastlistener.startListening)
        rcv_thread.daemon = True
        rcv_thread.start()
        time.sleep(1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)
        #ip = [(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
        #print "Local IP: ", ip
        print "Sending message..."
        sent = False
        while not sent:
            print "Trying to send..."
            sent = sock.sendto(data + "\n", (host, port))
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,0)
        print "Message sent!"
        #data, addr = sock.recvfrom(6)
        #print "Response from ", addr
        sock.close()

    #udpbroadcastlistener.startListening()
    time.sleep(2)
    cleanExit()

def cleanExit():
    if sock:
        print "Closing socket before quitting..."
        if sock:
            sock.close()
    udpbroadcastlistener.stopListening()
    print "Done! Bye bye..."


if __name__ == '__main__':
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        main()
    except KeyboardInterrupt:
        cleanExit()