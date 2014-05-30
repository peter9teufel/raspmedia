import socket
import os, sys
import threading
import Image
from constants import *


def readInt(data):
    intBytes = data[:4]
    remainingData = data[4:]
    num = (intBytes[0] << 24) + (intBytes[1] << 16) + (intBytes[2] << 8) + intBytes[3]
    return num, remainingData

def readString(data):
    size, data = readInt(data)
    strBytes = data[:size]
    remainingData = data[size:]
    inStr = str(strBytes)
    return inStr, remainingData


def _openSocket():
    global s
    s = socket.socket()
    s.bind(('',60020))
    s.listen(10) # Accept max. 10 connections
    print "File socket ready, listening for incoming file connections..."
    while True:
        sc, address = s.accept()
        print "TCP CLIENT CONNECTED: ", address

        dataSizeBytes = sc.recv(4)
        dataSize, remaining = readInt(bytearray(dataSizeBytes))
        print "Receiving %d Bytes" % (dataSize)
        buff = ''
        while len(buff) < dataSize:
            buff += sc.recv(1024)

        print "Closing TCP Client connection..."
        sc.close()

        print "Data read to buffer, processing bytearray..."

        data = bytearray(buff)
        # read number of files
        #numFilesBytes = sc.recv(4)
        numFiles, data = readInt(data)
        print "READING %d FILES" % numFiles
        for i in range(numFiles):
            # read file name
            #nameSizeBytes = sc.recv(4)
            #nameSize, data = readInt(data)
            #name = sc.recv(nameSize)
            name, data = readString(data)
            #print "READING FILE: ", name
            openPath = os.getcwd() + '/media/' + name
            #fileSizeBytes = sc.recv(4)
            fileSize, data = readInt(data)
            #print "FILESIZE: ", fileSize
            if not os.path.isdir(openPath):
                f = open(openPath, 'w+') #open in binary
                #l=''
                #while len(l)< fileSize:
                #    l += sc.recv(1024)
                l = data[:fileSize]
                data = data[fileSize:]
                f.write(l) 
                #print 'Bytes written to file: ', fileSize
                f.close()
                #print "File saved!"
        print "FILES SAVED!"

def openFileSocket():
    global server_thread
    # Start a thread with the server
    server_thread = threading.Thread(target=_openSocket)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    print "File socket loop running in thread:", server_thread.name


def closeFileSocket():
    global s
    s.close()


server_thread = None
s = None
