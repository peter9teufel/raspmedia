import socket
import sys, os


def sendFile(filePath, host):
	s = socket.socket()
	s.connect((host,60020))

	f=open (filePath, "rb")
	filename = os.path.basename(f.name)
	
	fnSize = len(filename)

	sizeBytes = [int(fnSize >> i & 0xff) for i in (24,16,8,0)]
	data = bytearray()
	for b in sizeBytes:
		data.append(int(b))

	s.send(data)
	s.send(filename)

	l = f.read(1024)
	while (l):
	    s.send(l)
	    l = f.read(1024)
	s.close()