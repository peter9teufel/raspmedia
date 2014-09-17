import socket
import sys, os, platform
import messages
from packages.rmmedia import mediaplayer

observers = []
_BLOCK_SIZE = 1024
def sendFile(filePath, host):
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
	s.send(data)
	s.send(filenameEnc)

	bytesSent = 0;
	l = f.read(_BLOCK_SIZE)
	while (l):
	    s.send(l)
	    bytesSent += _BLOCK_SIZE
	    if bytesSent > filesize:
	    	bytesSent = filesize
	    l = f.read(_BLOCK_SIZE)
	s.close()


def sendFiles(files, basePath, host):
	s = socket.socket()
	s.connect((host,60020))

	msgData = messages.getTcpFileMessage(files, basePath)
	if dlgMessageBuild:
		dlgMessageBuild.Update(100)

	msgSize = len(msgData)
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
		index += _BLOCK_SIZE

	s.close()

def sendAllImageFiles(host):
    mediaPath = "/home/pi/raspmedia/Raspberry/media"
    imgs = mediaplayer.getImageFilelist()
    sendFiles(imgs, mediaPath, host)
