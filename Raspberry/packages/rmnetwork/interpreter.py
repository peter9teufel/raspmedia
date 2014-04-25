import threading
from constants import *
from packages.rmconfig import configtool


def interpret(msg_data):
	print "Interpreting incoming data..."
	
	# initialize with error state
	result = INTERPRETER_ERROR

	data = bytearray(msg_data)
	size, data = readInt(data)
	print "Size: " + str(size)
	
	flag, data = readShort(data)
	print "Flag: " + str(flag)
	if flag == CONFIG_UPDATE:
		data = readConfigUpdate(data)
		result = INTERPRETER_SUCCESS
	elif flag == PLAYER_START:
		from packages.rmmedia import mediaplayer
		print 'UDP COMMAND Mediaplayer start...'
		mediaplayer.playerState = PLAYER_STARTED
		mediaplayer.play()
		result = INTERPRETER_SUCCESS
	elif flag == PLAYER_STOP:
		from packages.rmmedia import mediaplayer
		print 'UDP COMMAND Mediaplayer stop...'
		mediaplayer.playerState = PLAYER_STOPPED
		mediaplayer.stop()
		result = INTERPRETER_SUCCESS
	elif flag == SERVER_REQUEST:
		data = None
		result = INTERPRETER_SERVER_REQUEST
	elif flag == FILELIST_REQUEST:
		result = INTERPRETER_FILELIST_REQUEST
	elif flag == FILELIST_RESPONSE:
		readFileList(data)
		result = INTERPRETER_FILELIST_REQUEST

	#print "Remaining data: " + data.decode("utf-8")

	return result

def readFileList(data):
	numFiles, data = readInt(data)
	files = []
	for i in range(numFiles):
		file, data = readString(data)
		if file:
			files.append(file)
	print "FILE LIST READ: ", files

def readConfigUpdate(data):
	print "Current config: ", configtool.config
	print "Processing config update message..."
	key, data = readString(data)
	value, data = readConfigValue(data, key)
	print "New Key/Value Pair:"
	print "KEY: ", key
	print "VALUE: ", value
	return data

def readConfigValue(data, key):
	if key == 'image_interval' or key == 'image_enabled' or key == 'video_enabled' or key == 'shuffle' or key == 'repeat':
		# integer config value
		value, data = readInt(data)
	else:
		# string config value
		value, data = readString(data)
	return value, data

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