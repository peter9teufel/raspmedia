import socket
import sys, os, platform
import wx
import messages
from packages.lang.Localizer import *
if platform.system() == "Linux":
	from pubsub import pub as Publisher
else:
	from wx.lib.pubsub import pub as Publisher

observers = []
_BLOCK_SIZE = 1024
def sendFile(filePath, host, parent, isWindows=False):
	s = socket.socket()
	s.connect((host,60020))

	f=open (unicode(filePath), "rb")
	filename = os.path.basename(f.name)
	filenameEnc = filename.encode('utf-8')
	# print "Filename encoded: ", filenameEnc
	fnSize = len(filenameEnc)
	numFiles = 1
	numFilesBytes = [int(numFiles >> i & 0xff) for i in (24,16,8,0)]

	sizeBytes = [int(fnSize >> i & 0xff) for i in (24,16,8,0)]
	data = bytearray()
	for b in numFilesBytes:
		data.append(int(b))
	for b in sizeBytes:
		data.append(int(b))

	filesize = os.stat(filePath).st_size
	fileSizeBytes = [int(filesize >> i & 0xff) for i in (24,16,8,0)]
	for b in fileSizeBytes:
		data.append(int(b))
	# show progress dialog
	#prgDialog = wx.ProgressDialog("Sending...", "Sending file to player: " + filename, maximum = filesize, parent = parent, style = dlgStyle)
	prgDialog = wx.ProgressDialog(String("sending"), String("sending_files"), maximum = filesize, style = wx.PD_AUTO_HIDE)
	s.send(data)
	s.send(filenameEnc)

	bytesSent = 0;
	l = f.read(_BLOCK_SIZE)
	while (l):
	    s.send(l)
	    bytesSent += _BLOCK_SIZE
	    if bytesSent > filesize:
	    	bytesSent = filesize
	    prgDialog.Update(bytesSent)
	    l = f.read(_BLOCK_SIZE)
	s.close()
	prgDialog.Update(filesize)
	if isWindows:
		prgDialog.Destroy()


def sendFiles(files, basePath, host, parent, isWindows=False):
	s = socket.socket()
	s.connect((host,60020))

	dlgMessageBuild = None
	if len(files) > 5:
		dlgMessageBuild = wx.ProgressDialog(String("preparing"), String("preparing_data"), style = wx.PD_AUTO_HIDE)
		dlgMessageBuild.Pulse()
	msgData = messages.getTcpFileMessage(files, basePath)
	if dlgMessageBuild:
		dlgMessageBuild.Update(100)
		if isWindows:
			dlgMessageBuild.Destroy()
	msgSize = len(msgData)
	print "File message size: ", msgSize
	prgDialog = wx.ProgressDialog(String("sending"), String("sending_files"), maximum = msgSize, style = wx.PD_AUTO_HIDE)
	bytesSent = 0;
	index = 0
	while bytesSent < msgSize:
		packEnd = index + _BLOCK_SIZE
		# print "INDEX: %d PACKEND: %d MESSAGE SIZE: %d" % (index,packEnd,msgSize)
		if packEnd > msgSize:
			curPacket = msgData[index:]
		else:
			curPacket = msgData[index:packEnd]

		s.send(curPacket)
		bytesSent += _BLOCK_SIZE
		if bytesSent > msgSize:
			bytesSent = msgSize
		prgDialog.Update(bytesSent)
		index += _BLOCK_SIZE

	s.close()
	prgDialog.Update(msgSize)
	if isWindows:
		prgDialog.Destroy()

def registerObserver(observer):
	if not observer in observers:
		observers.append(observer)

def removeObserver(observer):
	if observer in observers:
		observers.remove(observer)
