import socket, select, time
import interpreter, netutil

from constants import *

def stopListening():
	global observers
	print "Stopping UDP Broadcast Listening routine..."
	global sock, wait
	wait = False
	# notify observers that listening is stopped
	for observer in observers:
		if observer[0] == OBS_STOP:
			observer[1]()

	# clear observer list
	observers = []
	print "Done!"

def startListening():
	global observers
	print "UDP Broadcast Listener starting listening routine..."
	global sock, wait
	if not sock:
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind(('', UDP_PORT))

	wait = True

	print "INSIDE BROADCASTLISTENER:"
	print "Waiting for incoming data..."
	while wait:
		#result = select.select([sock],[],[])
		#print "Result from select - processing..."
		#rec, address = result[0][0].recvfrom(1024)
		rec, address = sock.recvfrom(1024)
		print "Incoming data from ", str(address)
		if not address[0] in netutil.ip4_addresses():
			print "Incoming data not from own broadcast --> processing..."
			result, response = interpreter.interpret(rec)
			if result == INTERPRETER_SERVER_REQUEST:
				print "Server request response - length: ", len(rec)
				print ":".join("{:02x}".format(ord(c)) for c in rec)
				print "Server address: ", str(address)
				print ""
				if response[1] == TYPE_RASPMEDIA_PLAYER:
					for observer in observers:
						if observer[0] == OBS_HOST_SEARCH:
							observer[1](address, response[0])
				time.sleep(1)
			elif result == INTERPRETER_FILELIST_REQUEST:
				print "File list received!"
				print response
				for observer in observers:
					if observer[0] == OBS_FILE_LIST:
						observer[1](address, response)
			elif result == CONFIG_REQUEST:
				print "Config data received:"
				for observer in observers:
					if observer[0] == OBS_CONFIG:
						observer[1](response)
				print response
			elif result == PLAYER_UPDATE_ERROR:
				print "Player update failed: " + response
				for observer in observers:
					if observer[0] == OBS_UPDATE:
						observer[1](response)
			elif result == PLAYER_BOOT_COMPLETE:
				print "Player BOOT_COMPLETE"
				for observer in observers:
					if observer[0] == OBS_BOOT_COMPLETE:
						observer[1]

def registerObserver(observer):
	global observers
	if not observer in observers:
		observers.append(observer)


def removeObserver(observer):
	global observers
	if observer in observers:
		observers.remove(observer)


sock = None
wait = True
# observers for receiving file list
observers = []
# observers to be notified when listener stops
stopObservers = []
