import socket
import sys, os
import wx

observers = []
_BLOCK_SIZE = 1024
def sendFile(filePath, host, parent):
	s = socket.socket()
	s.connect((host,60020))

	f=open (filePath, "rb")
	filename = os.path.basename(f.name)
	
	fnSize = len(filename)

	sizeBytes = [int(fnSize >> i & 0xff) for i in (24,16,8,0)]
	data = bytearray()
	for b in sizeBytes:
		data.append(int(b))

	filesize = os.stat(filePath).st_size

	# show progress dialog
	dlgStyle =  wx.PD_AUTO_HIDE
	prgDialog = wx.ProgressDialog("Sending...", "Sending file to player: " + filename, maximum = filesize, parent = parent, style = dlgStyle)


	s.send(data)
	s.send(filename)

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
	for observer in observers:
		observer(None)

def registerObserver(observer):
	if not observer in observers:
		observers.append(observer)

def removeObserver(observer):
	if observer in observers:
		observers.remove(observer)