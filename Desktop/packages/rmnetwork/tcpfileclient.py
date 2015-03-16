# -*- coding: utf-8 -*-
import socket
import sys, os, platform, re
from constants import *
import wx
import messages
from packages.lang.Localizer import *
if platform.system() == "Linux":
    from wx.lib.pubsub import setupkwargs
    from wx.lib.pubsub import pub as Publisher
else:
    from wx.lib.pubsub import pub as Publisher

observers = []
_BLOCK_SIZE = 8096
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
	prgDialog = wx.ProgressDialog(tr("sending"), tr("sending_files"), maximum = filesize, style = wx.PD_AUTO_HIDE)
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

	sendTcpFileMessage(files, basePath, s, isWindows)
	'''
	dlgMessageBuild = None
	dlgMessageBuild = wx.ProgressDialog(tr("preparing"), tr("preparing_data"), style = wx.PD_AUTO_HIDE)
	dlgMessageBuild.Pulse()
	msgData = messages.getTcpFileMessage(files, basePath)
	if dlgMessageBuild:
		dlgMessageBuild.Update(100)
		if isWindows:
			dlgMessageBuild.Destroy()
	msgSize = len(msgData)
	# print "File message size: ", msgSize
	prgDialog = wx.ProgressDialog(tr("sending"), tr("sending_files"), maximum = msgSize, style = wx.PD_AUTO_HIDE)
	bytesSent = 0;
	index = 0
	print "Sending " + str(msgSize) + " bytes:"
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

	'''
	s.close()

def registerObserver(observer):
	if not observer in observers:
		observers.append(observer)

def removeObserver(observer):
	if observer in observers:
		observers.remove(observer)

# MESSAGE CREATION

def sendTcpFileMessage(files, basePath, tcpSocket, isWindows=False):
	msgSize = getTcpMessageSize(files, basePath)
	
	prgDialog = wx.ProgressDialog(tr("sending"), tr("sending_files"), maximum = msgSize, style = wx.PD_AUTO_HIDE)
	bytesSent = 0;
	index = 0
	print "Sending " + str(msgSize) + " bytes:"
	
	numFiles = len(files)

	data = bytearray()
	# append msg size and num files
	data = appendInt(data, msgSize, False)
	data = appendInt(data, numFiles, False)
	
	for filename in files:
		filePath = os.path.join(basePath, filename)
		
		# append file type
		if filename.endswith((SUPPORTED_IMAGE_EXTENSIONS)):
			data = appendInt(data, FILE_TYPE_IMAGE)
		else:
			data = appendInt(data, FILE_TYPE_VIDEO)

		# append filename
		filename = makeStringPlayerSafe(filename)
		data = appendString(data, filename, sizeLE=False)
		fileSize = os.stat(filePath).st_size
		data = appendInt(data, fileSize, False)

		#send file info
		tcpSocket.send(data)
		bytesSent += len(data)
		prgDialog.Update(bytesSent, filename)
		# send file data in 1024B packs
		with open(unicode(filePath), 'rb') as curFile:
			fileData = curFile.read(_BLOCK_SIZE)
			while fileData:
				dSize = len(fileData)
				tcpSocket.send(fileData)
				bytesSent += dSize
				perc = int((bytesSent * 100) / fileSize)
				if bytesSent <= msgSize:
					prgDialog.Update(bytesSent)
				fileData = curFile.read(_BLOCK_SIZE)

		# reset file info data
		data = bytearray()

	prgDialog.Update(msgSize)	
	if isWindows:
		prgDialog.Destroy()

def getTcpMessageSize(files, basePath):
	size = 4 # num files
	for filename in files:
		size += 4 # file type
		msgFilename = makeStringPlayerSafe(filename)
		size += len(msgFilename) + 4 # file name
		fileSize = os.stat(os.path.join(basePath, filename)).st_size
		size += fileSize + 4 # data size plus data bytes
	return int(size)

def appendBytes(data, append, LE=False):
	if LE:
		for b in reversed(append):
			data.append(b)
	else:
		for b in append:
			data.append(b)
	return data

def appendInt(data, num, LE=True):
	sizeBytes = [hex(num >> i & 0xff) for i in (24,16,8,0)]
	sizeBytes = [int(num >> i & 0xff) for i in (24,16,8,0)]
	return appendBytes(data, sizeBytes, LE)

def appendString(data, str, sizeLE=True):
	strByte = []
	try:
		strBytes = bytearray(str, 'utf-8')
	except:
		strBytes = bytearray(str)
	data = appendInt(data, len(strBytes), sizeLE)
	return appendBytes(data, strBytes)

def makeStringPlayerSafe(string):
	# replace whitespaces due to compatibility with omxplayer
	string = re.sub('[ ]', '_', string)
	# replace special characters
	string = re.sub(u'[ö]', 'oe', string)
	string = re.sub(u'[ä]', 'ae', string);
	string = re.sub(u'[ü]', 'ue', string);
	string = re.sub(u'[!@#$%&§+*]', '', string);
	return string
