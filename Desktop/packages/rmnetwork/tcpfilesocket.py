import socket
import os, sys, platform, time, threading, shutil
from PIL import Image, ImageDraw
import wx
import io
import binascii
if platform.system() == "Linux":
    from wx.lib.pubsub import setupkwargs
    from wx.lib.pubsub import pub as Publisher
else:
    from wx.lib.pubsub import pub as Publisher

from packages.lang.Localizer import *

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
    global s, prgDialog, windows, parent
    s = socket.socket()
    s.bind(('',60029))
    s.listen(10) # Accept max. 10 connections
    sc, address = s.accept()

    dataSizeBytes = sc.recv(4)
    dataSize, remaining = readInt(bytearray(dataSizeBytes))

    prgDialog.Update(100)
    if windows:
        prgDialog.Destroy()

    prgDialog = wx.ProgressDialog(tr("player_connected"), tr("receiving_files"), style=wx.PD_AUTO_HIDE, maximum=dataSize)

    buff = ''
    buff += sc.recv(dataSize)
    while len(buff) < dataSize:
        buff += sc.recv(1024)
        prg = len(buff)
        if prg > dataSize:
            prg = dataSize
        prgDialog.Update(prg)

    if windows:
        prgDialog.Destroy()

    sc.close()


    prgDialog = wx.ProgressDialog(tr("saving_previews"), tr("msg_saving_previews"), style=wx.PD_AUTO_HIDE)
    prgDialog.Pulse()

    data = bytearray(buff)
    # read number of files
    #numFilesBytes = sc.recv(4)
    numFiles, data = readInt(data)
    from os.path import expanduser
    home = expanduser("~")
    appPath = home + '/.raspmedia/'
    tmp = appPath + 'tmp/'
    if not os.path.isdir(appPath):
        os.mkdir(appPath)
    if not os.path.isdir(tmp):
        os.mkdir(tmp)
    tmpPath = tmp + address[0] + '/'
    if os.path.isdir(tmpPath):
        # print "Removing old temp directory..."
        shutil.rmtree(tmpPath)
    try:
        os.makedirs(tmpPath)
    except OSError as exception:
        # print "Exception in creating DIR: ",exception
        pass

    rFiles = []
    for i in range(numFiles):
        name, data = readString(data)
        openPath = tmpPath + name
        fileSize, data = readInt(data)
        if not os.path.isdir(openPath):
            l = data[:fileSize]
            data = data[fileSize:]
            if platform.system() == "Windows":
                stream = io.BytesIO(l)
                img = Image.open(stream)
                draw = ImageDraw.Draw(img)
                img.save(openPath)
            else:
                f = open(openPath, 'w+') #open in binary
                f.write(l)
                f.close()
        rFiles.append({"img_name": name, "img_path": tmpPath, "checked": False})

    prgDialog.Update(100)
    if windows:
        prgDialog.Destroy()

    closeFileSocket()

    # tell UI that file loading is done
    wx.CallAfter(Publisher.sendMessage, 'remote_files_loaded', files=rFiles)


def openFileSocket(parentElem, isWindows):
    global prgDialog, windows, parent
    parent = parentElem
    windows = isWindows
    prgDialog = wx.ProgressDialog(tr("loading_files"), tr("receiving_files"), style=wx.PD_AUTO_HIDE)
    prgDialog.Pulse()
    global server_thread
    # Start a thread with the server
    server_thread = threading.Thread(target=_openSocket)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()


def closeFileSocket():
    global s
    s.close()

prgDialog = None
windows = False
parent = None
server_thread = None
s = None
