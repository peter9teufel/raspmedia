import constants
from rmconfig import configtool

def interpret(msg_data):

	print "Interpreting incoming data: ", msg_data
	
	# initialize with error state
	result = constants.INTERPRET_ERROR

	data = bytearray(msg_data)
	size, data = readInt(data)
	print "Size: " + str(size)
	
	flag, data = readShort(data)
	print "Flag: " + str(flag)
	if flag == constants.CONFIG_UPDATE:
		data = readConfigUpdate(data)
		result = constants.INTERPRET_SUCCESS
	elif flag == constants.SERVER_REQUEST:
		result = constants.INTERPRET_SUCCESS_SERVER_REQUEST

	print "Remaining data: " + data.decode("utf-8")

	return result

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