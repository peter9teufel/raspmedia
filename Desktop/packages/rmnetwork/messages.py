import sys, os
from constants import *

def appendBytes(data, append, LE=False):
	if LE:
		for b in reversed(append):
			data.append(int(b))
	else:
		for b in append:
			data.append(int(b))
	return data

def appendInt(data, num, LE=True):
	sizeBytes = [hex(num >> i & 0xff) for i in (24,16,8,0)]
	sizeBytes = [int(num >> i & 0xff) for i in (24,16,8,0)]
	return appendBytes(data, sizeBytes, LE)

def appendShort(data, num, LE=True):
	sizeBytes = [int(num >> i & 0xff) for i in (8,0)]
	return appendBytes(data, sizeBytes, LE)

def appendString(data, str):
	strBytes = bytearray(str)
	data = appendInt(data, len(strBytes))
	return appendBytes(data, strBytes)


def appendArg(data, type, arg):
	if type == '-f':
		print "Saving FLAG"
		global flag
		flag = int(arg)
	elif type == '-w':
		print "Appending SHORT"
		appendShort(data, int(arg))
	elif type == '-s':
		print "Appending STRING"
		appendString(data, arg)
	elif type == '-i':
		print "Appending INT"
		appendInt(data, int(arg))

def getConfigUpdateMessage(key, value):
	data = bytearray()
	usgData = bytearray()

	appendString(usgData, str(key))
	print "KEY APPENDED!"
	if isinstance(value, (int)):
		print "New config value is appended as INT!"
		appendInt(usgData, value)
	else:
		appendString(usgData, value)

	size = 6 + len(usgData)

	appendInt(data, size)
	appendShort(data, CONFIG_UPDATE)
	appendBytes(data, usgData)

	print "Config message size: ", size
	return data

def getMessage(flag, args=None):
	# append all arguments given as cmd args to usgData
	usgData = None
	if args:
		usgData = bytearray()
		print args
		for i in range(0,len(args)):
			arg = args[i]
			print "Current arg: ", arg
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

def getTcpFileMessage(files, basePath):
	numFiles = len(files)

	data = bytearray()
	appendInt(data, numFiles)

	for filename in files:
		filePath = basePath + '/' + filename

		f=open (unicode(filePath), "rb")
		appendString(data, str(filename))

		filesize = os.stat(filePath).st_size
		appendInt(data, filesize)
		fileData = f.read(1024)
		while fileData:
			appendBytes(data, fileData)
			fileData = r.read(1024)
	return data