import socket, select
import interpreter, constants

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

	while wait:
		print "INSIDE BROADCASTLISTENER:"
		print "Waiting for incoming data..."
		
		#result = select.select([sock],[],[])
		#print "Result from select - processing..."
		#rec, address = result[0][0].recvfrom(1024)
		
		rec, address = sock.recvfrom(1024)
		if interpreter.interpret(rec) == constants.INTERPRET_SUCCESS_SERVER_REQUEST:
			print "Server request response - length: ", len(rec)
			print "Server address: ", str(address)


sock = None
wait = True