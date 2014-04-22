import struct
from rmconfig import configtool

# predefined message flags
CONFIG_UPDATE = 0x00
PLAYER_START = 0x01
PLAYER_STOP = 0x02

def interpret(msg_data):
	print "Interpreting incoming data: ", msg_data
	data = bytearray(msg_data)
	size, data = readInt(data)
	print "Size: " + str(size)
	
	flag, data = readShort(data)
	print "Flag: " + str(flag)
	if flag == CONFIG_UPDATE:
		readConfigUpdate(data)

	print "Remaining data: " + data.decode("utf-8")
	#print "Interpreting incoming data: ", struct.unpack("I", msg_data)[0]
	#print "Byte data: "
	#print struct.unpack("4b", msg_data)

def readConfigUpdate(data):
	print "Current config: ", configtool.config
	print "Processing config update message..."
	key, data = readString(data)
	value, data = readString(data)
	print "New Key/Value Pair: " + key + " - " + value

def readInt(data):
	intBytes = data[:4]
	remainingData = data[4:]
	num = (intBytes[0] << 24) + (intBytes[1] << 16) + (intBytes[2] << 8) + intBytes[3]
	return num, remainingData

def readShort(data):
	intBytes = data[:2]
	remainingData = data[2:]
	num = (intBytes[0] << 8) + intBytes[1]
	return num, remainingData

def readString(data):
	size, data = readInt(data)
	strBytes = data[:size]
	remainingData = data[size:]
	inStr = str(strBytes)
	return inStr, remainingData