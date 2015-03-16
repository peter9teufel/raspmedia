import platform, threading, socket, select, time
import interpreter, netutil
import wx
if platform.system() == "Linux":
    from wx.lib.pubsub import setupkwargs
    from wx.lib.pubsub import pub as Publisher
else:
    from wx.lib.pubsub import pub as Publisher
from constants import *


class UDPResponseListener(threading.Thread):
	def __init__(self):
		self.run_event = threading.Event()
		threading.Thread.__init__(self, name="UDP_ResponseListener_Thread")

	def run(self):
		global timeout
		while run:
			self.run_event.wait()
			global observers
			# print "UDP Broadcast Listener starting listening routine..."
			global sock, wait
			if not sock:
				sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				sock.bind(('', UDP_PORT))
			sock.settimeout(timeout)
			# reset variables
			rec = None
			address = None
			try:
				rec, address = sock.recvfrom(4048)
			except:
				# print "Timeout catched..."
				pass

			if rec and address:
				# print "Incoming data from ", str(address)
				if not address[0] in netutil.ip4_addresses():
					# print "Incoming data not from own broadcast --> processing..."
					result, response = interpreter.interpret(rec)
					if result == INTERPRETER_SERVER_REQUEST:
						print "RaspMedia player found: ", str(address)
						if response[1] == TYPE_RASPMEDIA_PLAYER:
							wx.CallAfter(Publisher.sendMessage, 'host_found', host=address, playerName=str(response[0]), freeSpace=response[3])
					elif result == INTERPRETER_FILELIST_REQUEST:
						wx.CallAfter(Publisher.sendMessage, 'remote_files', serverAddr=address, files=response)
					elif result == CONFIG_REQUEST:
						wx.CallAfter(Publisher.sendMessage, 'config', config=response)
					elif result == GROUP_CONFIG_REQUEST:
						wx.CallAfter(Publisher.sendMessage, 'group_config', group_config=response, playerIP=address[0])
					elif result == PLAYER_UPDATE_ERROR:
						wx.CallAfter(Publisher.sendMessage, 'update_failed')
					elif result == PLAYER_BOOT_COMPLETE:
						wx.CallAfter(Publisher.sendMessage, 'boot_complete')
						stopListening()
					elif result == GROUP_CONFIG_ADD_ACTION:
						wx.CallAfter(Publisher.sendMessage, 'action_saved')
					elif result == GROUP_CONFIG_ACTION_DELETE:
						wx.CallAfter(Publisher.sendMessage, 'action_deleted')
					elif result == DISK_INFO_REQUEST:
						wx.CallAfter(Publisher.sendMessage, 'disk_info', diskInfo=response)


def stopListening():
	global listener, observers
	global sock, wait

	wx.CallAfter(Publisher.sendMessage, 'listener_stop')

	if listener:
		listener.run_event.clear()

def startListening():
	global listener
	if not listener:
		listener = UDPResponseListener()
		listener.start()
	listener.run_event.set()

def destroy():
	global run, listener, timeout
	# clear flag for listener thread run loop
	run = False
	# if listener currently not running --> set short timeout and runevent
	timeout = 0.1
	listener.run_event.set()

def setTimeout(newTimeout):
	global timeout
	timeout = newTimeout

sock = None
timeout = UDP_RESPONSE_TIMEOUT
listener = None
run = True
