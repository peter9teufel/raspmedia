import sys, threading, time
import socket, select
import messages
import udpbroadcastlistener

def main():
	global sock
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
	while True:
	 	flag = 0


if __name__ == '__main__':
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		main()
	except KeyboardInterrupt:
		if sock:
			print "Closing socket before quitting..."
			if sock:
				sock.close()
			udpbroadcastlistener.stopListening()
			print "Done! Bye bye..."