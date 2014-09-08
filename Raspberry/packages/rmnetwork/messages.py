import sys
from packages.rmconfig import configtool
from constants import *

def appendBytes(data, append, LE=False):
	if LE:
		for b in reversed(append):
			data.append(int(b))
	else:
		for b in append:
			data.append(int(b))
	return data

def appendInt(data, num):
	sizeBytes = [int(num >> i & 0xff) for i in (24,16,8,0)]
	return appendBytes(data, sizeBytes, True)

def appendShort(data, num):
	sizeBytes = [int(num >> i & 0xff) for i in (8,0)]
	return appendBytes(data, sizeBytes, True)

def appendString(data, str):
	strBytes = bytearray(str)
	data = appendInt(data, len(strBytes))
	return appendBytes(data, strBytes)


def appendArg(data, type, arg):
	if type == '-f':
		#print "Saving FLAG"
		global flag
		flag = int(arg)
	elif type == '-w':
		#print "Appending SHORT"
		appendShort(data, int(arg))
	elif type == '-s':
		#print "Appending STRING"
		appendString(data, arg)
	elif type == '-i':
		#print "Appending INT"
		appendInt(data, int(arg,0))

def getConfigMessage():
	config = configtool.readConfig()
	configStr = str(config)
	#print "Building message for CONFIG:"
	#print configStr
	confBytes = bytearray(configStr)

	data = bytearray()
	size = 10 + len(confBytes)
	appendInt(data, size)
	appendShort(data, CONFIG_REQUEST)
	appendInt(data, len(confBytes))
	appendBytes(data, confBytes)

	#print "Message size: ", size
	return data

def getGroupConfigMessage():
	config = configtool.readGroupConfig()
	configStr = str(config)
	confBytes = bytearray(configStr)

	data = bytearray()
	size = 10 + len(confBytes)
	appendInt(data, size)
	appendShort(data, GROUP_CONFIG_REQUEST)
	appendInt(data, len(confBytes))
	appendBytes(data, confBytes)

	return data


def getMessage(flag, args=None):
	# append all arguments given as cmd args to usgData
	usgData = bytearray()
	if args:
		# print args
		for i in range(0,len(args)):
			arg = args[i]
			#print "Current arg: ", arg
			if arg.startswith('-'):
				if i < len(args) - 1:
					appendArg(usgData, arg, args[i+1])

	# combine msg size and usgData in final message to send in data
	data = bytearray()
	size = 6
	if usgData:
		size += len(usgData)
	appendInt(data, size)
	appendShort(data, flag)
	if usgData:
		appendBytes(data, usgData)

	print "Message size: ", size
	return data
