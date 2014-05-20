import sys, threading, time
import socket, select
import netutil
from constants import *

def sendBroadcast(data):
	ips = netutil.ip4_addresses()
	for ip in ips:
		print "Broadcasting over IP ",ip
		_sendMessage(data,ip)
	cleanExit()

def _sendMessage(data,local_bind=None):
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
		print "Sending message..."
		sent = False
		while not sent:
			sent = sock.sendto(data + "\n", ('<broadcast>', port))
		print "Message sent: ",sent
		sock.close()


def cleanExit():
	global sock
	if sock:
		print "Closing socket before quitting..."
		if sock:
			sock.close()
	print "Done! Bye bye..."

# global socket variable
sock = None
