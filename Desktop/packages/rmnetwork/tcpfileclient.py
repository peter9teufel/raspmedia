import socket
import sys, os
import wx
import messages
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

	# show progress dialog
	#prgDialog = wx.ProgressDialog("Sending...", "Sending file to player: " + filename, maximum = filesize, parent = parent, style = dlgStyle)
	prgDialog = wx.ProgressDialog("Sending...", "Sending file to player: " + filename, maximum = filesize, style = wx.PD_AUTO_HIDE)
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

	prgDialog = wx.ProgressDialog("Sending...", "Sending file to player: " + filename, maximum = filesize, style = wx.PD_AUTO_HIDE)
	msgData = messages.getTcpFileMessage(files, basePath)
	msgSize = len(msgData)
	bytesSent = 0;
	index = 0
	while index < msgSize:
		packEnd = index + _BLOCK_SIZE
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
