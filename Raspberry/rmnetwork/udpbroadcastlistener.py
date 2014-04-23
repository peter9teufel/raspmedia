import socket, select
import interpreter

from constants import *

def stopListening():
	print "Stopping UDP Broadcast Listening routine..."
	global wait
	wait = False
	if sock:
		sock.close()
	print "Done!"

def startListening():
	print "UDP Broadcast Listener starting listening routine..."
	global sock
	global wait
	if not sock:
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind(('', 60007))
		
	wait = True

	print "INSIDE BROADCASTLISTENER:"
	print "Waiting for incoming data..."
	while wait:	
		#result = select.select([sock],[],[])
		#print "Result from select - processing..."
		#rec, address = result[0][0].recvfrom(1024)
		rec, address = sock.recvfrom(1024)
		if interpreter.interpret(rec) == INTERPRETER_SERVER_REQUEST:
			print "Server request response - length: ", len(rec)
			print "Server address: ", str(address)
			print ""
		elif interpreter.interpret(rec) == INTERPRETER_FILELIST_REQUEST:
			print "File list received!"
sock = None
wait = True