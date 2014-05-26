import sys, threading, time
import socket, select
import messages, udpresponselistener, netutil
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

def sendMessage(data,host='<broadcast>',response_timeout=None):
	if host == '<broadcast>':
		ips = netutil.ip4_addresses()
		for ip in ips:
			print "Broadcasting over IP ",ip
			_sendMessage(data,host,ip,response_timeout)
	else:
		_sendMessage(data,host,None,response_timeout)
	# ensure a clean exit when data is sent and response processed
	#cleanExit()
	#if not response_timeout:
	#	cleanExit()

def _sendMessage(data,host,local_bind=None,response_timeout=None):
	global sock
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	port = UDP_PORT
	# if valid message data present --> send it
	if data:
		print "Creating socket..."
		# SOCK_DGRAM is the socket type to use for UDP sockets

		sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)
		if local_bind:
			sock.bind((local_bind, 29885))

		print "Starting response listener in background thread..."
		# wait a given timeout for a network response
		timeout = UDP_RESPONSE_TIMEOUT
		if response_timeout:
			timeout = response_timeout
		else:
			if host == '<broadcast>' or local_bind:
				print "Using longer Broadcast Timeout..."
				timeout = UDP_BROADCAST_RESPONSE_TIMEOUT
				#time.sleep(UDP_BROADCAST_RESPONSE_TIMEOUT)
			else:
				pass
				#time.sleep(UDP_RESPONSE_TIMEOUT)
		# start timer to stop listener after timeout
		t = threading.Timer(timeout, udpresponselistener.stopListening)
		t.start()
		# set timeout in listener and start it
		udpresponselistener.setTimeout(timeout)
		udpresponselistener.startListening()

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

def cleanExit():
	if sock:
		print "Closing socket before quitting..."
		if sock:
			sock.close()
	#udpresponselistener.stopListening()
	print "Done! Bye bye..."

# global socket variable
sock = None

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		cleanExit()
