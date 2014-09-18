import socket
import os, sys, time, threading
import Image
from packages.rmmedia import mediaplayer
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

        # check thumbnails path
        thumbsPath = os.getcwd() + '/media/thumbs/'
        if not os.path.isdir(thumbsPath):
            os.mkdir(thumbsPath)

        print "READING %d FILES" % numFiles
        for i in range(numFiles):
            # read file name
            name, data = readString(data)
            openPath = os.getcwd() + '/media/' + name
            fileSize, data = readInt(data)
            if not os.path.isdir(openPath):
                f = open(openPath, 'w+') #open in binary
                l = data[:fileSize]
                data = data[fileSize:]
                f.write(l)
                f.close()

                # save thumbnail
                img = Image.open(openPath)
                w = img.size[0]
                h = img.size[1]
                newW = 200
                newH = newW * h / w
                img.thumbnail((newW,newH))
		img.save(thumbsPath + name)
        print "FILES SAVED!"
        
        if mediaplayer.playerState == PLAYER_STARTED:
            mediaplayer.stop()
            time.sleep(3)
            mediaplayer.play()

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
