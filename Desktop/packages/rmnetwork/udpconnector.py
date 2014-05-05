import sys, threading, time
import socket, select
import messages, udpresponselistener
from constants import *

def main():
	data = None
	flag = -1

	if len(sys.argv) > 3:
		flag = int(sys.argv[2])
		args = sys.argv[3:]
		data = messages.getMessage(flag, args)
	elif len(sys.argv) == 3:
		flag = int(sys.argv[2])
		data = messages.getMessage(flag)

	if data and not flag == -1:
		sendMessage(data)

def sendMessage(data,host='<broadcast>'):
	global sock
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	port = 60005


	# if valid message data present --> send it
	if data:
		print "Creating socket..."
		# SOCK_DGRAM is the socket type to use for UDP sockets
		print "Starting broadcast response listening thread..."
		rcv_thread = threading.Thread(target=udpresponselistener.startListening)
		rcv_thread.daemon = True
		rcv_thread.start()
		#time.sleep(UDP_RESPONSE_TIMEOUT)
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

	# wait a given timeout for a network response
	time.sleep(UDP_RESPONSE_TIMEOUT)
	cleanExit()

def cleanExit():
	if sock:
		print "Closing socket before quitting..."
		if sock:
			sock.close()
	udpresponselistener.stopListening()
	print "Done! Bye bye..."

# global socket variable
sock = None

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		cleanExit()