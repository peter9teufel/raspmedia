import threading
from constants import *


def interpret(msg_data):
	print "Interpreting incoming data..."
	
	# initialize with error state
	result = INTERPRETER_ERROR

	data = bytearray(msg_data)
	size, data = readInt(data)
	print "Size: " + str(size)
	
	flag, data = readShort(data)
	returnData = None
	print "Flag: " + str(flag)
	if flag == SERVER_REQUEST:
		data = None
		result = INTERPRETER_SERVER_REQUEST
	elif flag == FILELIST_REQUEST:
		result = INTERPRETER_FILELIST_REQUEST
	elif flag == FILELIST_RESPONSE:
		returnData = readFileList(data)
		result = INTERPRETER_FILELIST_REQUEST
	elif flag == CONFIG_REQUEST:
		result = CONFIG_REQUEST
		returnData = readConfigData(data)

	#print "Remaining data: " + data.decode("utf-8")

	return result, returnData

def readConfigData(data):
	config, data = readString(data)
	return config

def readFileList(data):
	numFiles, data = readInt(data)
	files = []
	for i in range(numFiles):
		file, data = readString(data)
		if file:
			files.append(file)
	return files

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