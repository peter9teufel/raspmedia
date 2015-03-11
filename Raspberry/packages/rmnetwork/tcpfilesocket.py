import socket
import os, sys, time, threading, shutil, time
import Image, ImageDraw
import io
from packages.rmmedia import mediaplayer
from constants import *


def readInt(data):
    intBytes = data[:4]
    if len(data) > 4:
        remainingData = data[4:]
    else:
        remainingData = []
    num = (intBytes[0] << 24) + (intBytes[1] << 16) + (intBytes[2] << 8) + intBytes[3]
    return num, remainingData

# added size!
def readString(data, size):
    #size, data = readInt(data)
    strBytes = data[:size]
    if len(data) > size:
        remainingData = data[size:]
    else:
        remainingData = []
    inStr = str(strBytes)
    return inStr, remainingData


def interpret(tmpFilePath):
    # open temp file in binary mode
    with open(tmpFilePath, 'rb') as f:
        data = bytearray(f.read(4))
        numFiles, data = readInt(data)

        # check thumbnails path
        thumbsPath = os.path.join(os.getcwd(), '/media/thumbs/')
        if not os.path.isdir(thumbsPath):
            os.mkdir(thumbsPath)

        isImage = False
        print "READING %d FILES" % numFiles
        for i in range(numFiles):
            # read file type
            data = bytearray(f.read(4))
            fileType, data = readInt(data)
            if fileType == FILE_TYPE_IMAGE:
                isImage = True
            else:
                isImage = False
            # read file name
            data = bytearray(f.read(4))
            size, data = readInt(data)
            data = bytearray(f.read(size))
            name, data = readString(data, size)
            openPathDir = os.getcwd() + '/media/'
            openPath = os.path.join(openPathDir, name)
            data = bytearray(f.read(4))
            fileSize, data = readInt(data)
            if not os.path.isdir(openPath):
                #f = open(openPath, 'w+') #open in binary
                l = bytearray(f.read(fileSize))
                if isImage:
                    stream = io.BytesIO(l)
                    img = Image.open(stream)
                    draw = ImageDraw.Draw(img)
                    img.save(openPath)
                else:
                    with open(openPath, 'w+') as newFile:
                        newFile.write(l)
    # remove temp file
    os.remove(tmpFilePath)
    checkThumbnails()

def checkThumbnails():
    print "Checking thumbnails..."
    mediaPath = os.getcwd() + '/media/'
    thumbPath = mediaPath + 'thumbs/'

    if not os.path.isdir(thumbPath):
        os.mkdir(thumbPath)
    cnt = 0
    files = mediaplayer.getImageFilelist()
    for name in files:
        oPath = os.path.join(mediaPath, name)
        tPath = os.path.join(thumbPath, name)
        if not os.path.isfile(tPath):
            # no thumbnail for image present -> create and save thumbnail
            img = Image.open(oPath)
            w = img.size[0]
            h = img.size[1]
            newW = 200
            newH = newW * h / w
            img.thumbnail((newW,newH))
            img.save(os.path.join(thumbPath, name))
            cnt += 1
    print "%d missing thumbnails created and saved." % cnt

def _openSocket():
    # create temp directory for received data
    if os.path.isdir(TCP_TEMP):
        shutil.rmtree(TCP_TEMP)
    os.mkdir(TCP_TEMP)

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
        bytesRead = 0
        tmpFile = "tmp_" + str(int(round(time.time())))
        with open(TCP_TEMP + "/" + tmpFile, 'w') as tmp:
            while bytesRead < dataSize:
                data = sc.recv(1024)
                bytesRead += len(data)
                tmp.write(data)

        print "Closing TCP Client connection..."
        sc.close()

        print "Data read to buffer, processing..."
        interpret(TCP_TEMP + "/" + tmpFile)

        print "FILES SAVED!"

        if mediaplayer.playerState == PLAYER_STARTED:
            mediaplayer.stop()
            time.sleep(5)
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
