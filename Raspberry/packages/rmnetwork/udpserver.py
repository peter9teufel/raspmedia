import threading, time, subprocess
import SocketServer
import interpreter, messages, netutil, GroupManager, tcpfileclient

from packages.rmmedia import mediaplayer
from constants import *
from packages.rmconfig import configtool

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
        data = self.request[0]
        inData = self.request[0].strip()
        cSocket = self.request[1]
        curThread = threading.current_thread()
        if not self.client_address[0] in netutil.ip4_addresses():
            result, msg = interpreter.interpret(data, self.client_address[0])


            if result == SERVER_REQUEST:
                freeSpace = self.FreeDiskSpace()
                responseData = messages.getMessage(SERVER_REQUEST_ACKNOWLEDGE, ["-i", str(TYPE_RASPMEDIA_PLAYER), "-i", "0","-s", str(configtool.readConfig()['player_name']), "-i", str(freeSpace)])
                addr = (self.client_address[0], UDP_PORT)
                print "Sending response to client:"
                print (addr)
                if cSocket.sendto(responseData, addr):
                    print "Response sent!"
                else:
                    print "Sending response failed!"
            elif result == FILELIST_REQUEST:
                files = mediaplayer.getMediaFileList()
                args = ['-i', str(len(files))]
                for file in files:
                    args.append('-s')
                    args.append(file)
                responseData = messages.getMessage(FILELIST_RESPONSE,args)
                if cSocket.sendto(responseData, (self.client_address[0], UDP_PORT)):
                    print "Filelist sent!"
            elif result == CONFIG_REQUEST:
                responseData = messages.getConfigMessage()
                if cSocket.sendto(responseData, (self.client_address[0], UDP_PORT)):
                    print "Config sent!"
            elif result == GROUP_CONFIG_REQUEST:
                response = messages.getGroupConfigMessage()
                if cSocket.sendto(response, (self.client_address[0], UDP_PORT)):
                    print "Group Config sent!"
            elif result == GROUP_CONFIG_ADD_ACTION:
                    configtool.addGroupAction(msg)
                    gConf = configtool.readGroupConfig()
                    response = messages.getMessage(GROUP_CONFIG_ADD_ACTION)
                    if cSocket.sendto(response, (self.client_address[0], UDP_PORT)):
                        print "Action saved confirmation sent!"
                    GroupManager.ReInitGroupManager(gConf)
            elif result == GROUP_CONFIG_ACTION_DELETE:
                    configtool.deleteGroupAction(msg)
                    gConf = configtool.readGroupConfig()
                    response = messages.getMessage(GROUP_CONFIG_ACTION_DELETE)
                    if cSocket.sendto(response, (self.client_address[0], UDP_PORT)):
                        print "Action deleted confirmation sent!"
                    GroupManager.ReInitGroupManager(gConf)
            elif result == PLAYER_UPDATE_ERROR:
                responseData = messages.getMessage(PLAYER_UPDATE_ERROR, ["-s", str(msg)])
                cSocket.sendto(responseData, (self.client_address[0], UDP_PORT))
            elif result == FILE_DATA_REQUEST:
                # send images from player over tcp to host in separate thread to not block other udp handling
                t = threading.Thread(target=self.SendImagesOverTCP, args=[self.client_address[0]])
                t.daemon = True
                t.start()
        else:
            print "Received own broadcast... ignored."


        # DEBUG CODE to echo the received message
        # print "{} on {} wrote:".format(self.client_address[0], curThread.name)
        # print data
        # cSocket.sendto(data.upper(), self.client_address)

    def SendImagesOverTCP(self, host):
        time.sleep(0.5)
        tcpfileclient.sendAllImageFiles(host)

    def FreeDiskSpace(self):
        df = subprocess.Popen(["df", "/home/pi/raspmedia/Raspberry/rasp-mediaplayer.py"], stdout=subprocess.PIPE)
        output = df.communicate()[0]
        device, size, used, available, percent, mountpoint = output.split("\n")[1].split()
        return available

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


stop()
