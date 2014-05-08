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


def _openSocket():
    global s
    s = socket.socket()
    s.bind(('',60020))
    s.listen(10) # Accept max. 10 connections
    print "File socket ready, listening for incoming file connections..."
    while True:
        sc, address = s.accept()

        print address
        # read file name
        nameSizeBytes = sc.recv(4)
        nameSize, remaining = readInt(bytearray(nameSizeBytes))
        name = sc.recv(nameSize)
        print "RECEIVING FILE: ", name
        name = name.decode('utf-8')
        openPath = os.getcwd() + '/media/' + name
        if not os.path.isdir(openPath):
            f = open(openPath, 'w+') #open in binary


            l = sc.recv(1024)
            total = 1024;
            while (l):
                    f.write(l)
                    l = sc.recv(1024)
                    total += 1024
            print 'Bytes written to file: ', total
            f.close()
            print "File saved!"
            sc.close()
            _optimize(os.getcwd() + '/media/' + name)

def _optimize(filePath):
    if filePath.endswith((SUPPORTED_IMAGE_EXTENSIONS)):
        img = Image.open(filePath)
        maxW = 1920
        maxH = 1080
        w,h = img.size
        if w/h > 1.770:
            width = maxW
            height = maxW * h / w
        else:
            height = maxH
            width = maxH * w / h
        img.thumbnail((width, height))
        print "Saving optimized image..."
        print "W: ", width
        print "H: ", height
        img.save(filePath)

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
