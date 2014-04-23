import sys
import socket
import messages
import interpreter

data = None
flag = -1

if len(sys.argv) > 3:
	flag = int(sys.argv[2])
	args = sys.argv[3:]
	data = messages.getMessage(flag, args)
elif len(sys.argv) == 3:
	flag = int(sys.argv[2])
	data = messages.getMessage(flag)

host = '<broadcast>'
port = 60005

# if valid message data and flag present --> send it
if data and not flag == -1:
	# SOCK_DGRAM is the socket type to use for UDP sockets
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)
	sock.sendto(data + "\n", (host, port))

	if flag == 3: # Server request --> read response
		rec, address = sock.recvfrom(1024)
		print "Server request response - length: ", len(rec)
		print "Server address: ", str(address)
		print str(rec)
	
	sock.close()