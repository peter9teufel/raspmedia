import socket
import sys
import struct

def appendBytes(data, append):
	for b in append:
		data.append(int(b))
	return data

def appendInt(data, num):
	sizeBytes = [int(num >> i & 0xff) for i in (24,16,8,0)]
	return appendBytes(data, sizeBytes)

def appendShort(data, num):
	sizeBytes = [int(num >> i & 0xff) for i in (8,0)]
	return appendBytes(data, sizeBytes)

def appendString(data, str):
	strBytes = bytearray(str)
	data = appendInt(data, len(strBytes))
	return appendBytes(data, strBytes)

HOST, PORT = "localhost", 60005
# data = " ".join(sys.argv[1:])
# data = struct.pack("I", int(sys.argv[1]))
data = bytearray()


appendInt(data, 25)
appendShort(data, 0)
appendString(data, "image_interval")
appendString(data, str(4))

# SOCK_DGRAM is the socket type to use for UDP sockets
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# As you can see, there is no connect() call; UDP has no connections.
# Instead, data is directly sent to the recipient via sendto().
sock.sendto(data + "\n", (HOST, PORT))

sock.close()