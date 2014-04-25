import threading, time
import SocketServer
import interpreter, messages

from constants import *

server = None
server_thread = None

class MyUDPHandler(SocketServer.BaseRequestHandler):
    """
    This class works similar to the TCP handler class, except that
    self.request consists of a pair of data and client socket (cSocket), and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto().
    """

    def handle(self):
        data = self.request[0].strip()
        inData = self.request[0].strip()
        cSocket = self.request[1]
        curThread = threading.current_thread()
        result = interpreter.interpret(data)

        if result == INTERPRETER_SERVER_REQUEST:
            print "{} on {} wrote:".format(self.client_address[0], curThread.name)
            print "\nServer request received - sending response...\n"
            responseData = messages.getMessage(SERVER_REQUEST)
            addr = (self.client_address[0], UDP_PORT)
            #print "Response delay..."
            #time.sleep(1)
            print "Sending response to:"
            print (self.client_address[0], 60007)
            if cSocket.sendto(responseData, (self.client_address[0], 60007)):
                print "Response sent!"
            else:
                print "Sending response failed!"
        elif result == INTERPRETER_FILELIST_REQUEST:
            from rmmedia import mediaplayer
            files = mediaplayer.getMediaFileList()
            print files
            args = ['-i', '4']
            for file in files:
                args.append('-s')
                args.append(file)
            responseData = messages.getMessage(FILELIST_RESPONSE,args)
            if cSocket.sendto(responseData, (self.client_address[0], 60007)):
                print "Filelist sent!"
            
        # DEBUG CODE to echo the received message
        # print "{} on {} wrote:".format(self.client_address[0], curThread.name)
        # print data
        # cSocket.sendto(data.upper(), self.client_address)

def start():
    global server, server_thread
    if not server:
        server = SocketServer.UDPServer((UDP_HOST, UDP_PORT), MyUDPHandler)
        
    print "Starting server..."
    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    print "Server loop running in thread:", server_thread.name

def stop():
    global server
    if(server):
        print "Stopping server..."
        server.shutdown()
        print "Done!"


if __name__ == "__main__":
    print "Type commands any time -->"
    print "-- \"start\" to start UDP server"
    print "-- \"stop\" to stop close UDP server"
    print "-- \"quit\" exit program:"
    
    running = True
    while running:
        cmd = raw_input("")
        running = (cmd != "quit")
        if(cmd == "start"):
            start()
        elif(cmd == "stop"):
            stop()
stop()