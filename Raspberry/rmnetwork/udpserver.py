import threading
import SocketServer
import interpreter

UDP_HOST = ""
UDP_PORT = 60005
server = None
server_thread = None

class MyUDPHandler(SocketServer.BaseRequestHandler):
    """
    This class works similar to the TCP handler class, except that
    self.request consists of a pair of data and client socket, and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto().
    """

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        curThread = threading.current_thread()
        interpreter.interpret(data)
        # DEBUG CODE to echo the received message
        # print "{} on {} wrote:".format(self.client_address[0], curThread.name)
        # print data
        # socket.sendto(data.upper(), self.client_address)

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