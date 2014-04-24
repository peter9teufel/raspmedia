#! /usr/bin/env python

import os, threading, time, subprocess, re
from packages.rmutil import processtool
from packages.rmconfig import configtool
from constants import *

cwd = os.getcwd()
print "PLAYER CWD: " + cwd
mediaPath = ''
config = configtool.config
playerState = PLAYER_STOPPED

def getMediaFileList():
    files = []
    for file in os.listdir(mediaPath):
        if isImage(file) or isVideo(file):
            files.append(file)
    return files

def setMediaPath(curMediaPath):
    global mediaPath
    mediaPath = curMediaPath

def isImage(filename):
    supportedExtensions = ('.jpg', '.jpeg', '.JPG', '.JPEG', '.png', '.PNG')
    return filename.endswith((supportedExtensions))

def isVideo(filename):
    supportedExtensions = ('.mp4', '.m4v', '.mpeg', '.mpeg1', '.mpeg4')
    return filename.endswith((supportedExtensions))

def processImagesOnce():
    imgCmdList = ["sudo","fbi","-noverbose", "--once", "-t", str(config['image_interval']), "-blend", "400", "-T","2"]
    numImg = 0
    files = os.listdir(mediaPath)
    files.sort()
    for file in files:
        # check file extension
        if isImage(file):
            # process image file
            imgCmdList.append(mediaPath + file)
            numImg += 1
    print "Image command to call:"
    print imgCmdList
    subprocess.call(imgCmdList)
    duration = numImg * (config['image_interval'] + 2) + 1
    print "Number of images: ", numImg
    print "Sleeping duration: ", duration
    time.sleep(duration)

def fbiImageLoop():
    imgCmdList = ["sudo","fbi","-noverbose", "-t", str(config['image_interval']), "-blend", "400", "-T","2"]
    numImg = 0
    for file in os.listdir(mediaPath):
        # check file extension
        if isImage(file):
            # process image file
            imgCmdList.append(mediaPath + file)
            numImg += 1
    print "Image command to call:"
    print imgCmdList
    subprocess.call(imgCmdList)
    # wait in loop as fbi command does not block and check for config changes
    while config['repeat'] and playerState == PLAYER_STARTED:
        # estimate duration of one loop of all images
        duration = numImg + (config['image_interval'] + 2) + 1
        time.sleep(duration)
        # check for config changes after approximately each loop
        reloadConfig()


def processImagesOnly():
    print "Processing only images."
    if config['repeat']:
        fbiImageLoop()
    else:
        processImagesOnce()
    stop()

def processVideosOnce():
    global playerState
    for file in os.listdir(mediaPath):
        if playerState == PLAYER_STARTED:
            if isVideo(file):
                playVideo(file)

def processVideosOnly():
    print "Processing only videos."
    processVideosOnce()
    while config['repeat'] and playerState == PLAYER_STARTED:
        # check for config changes
        reloadConfig()
        processVideosOnce()
    stop()

def playVideo(file):
    global playerState
    # process video file -> omxplay will block until its done
    print "Status PLAYER_STARTED: ", playerState == PLAYER_STARTED
    if playerState == PLAYER_STARTED:
        print "Starting video file " + file
        subprocess.call([cwd + '/scripts/omxplay.sh', mediaPath + file])


def processAllFilesOnce():
    vidCommand = 'sudo omxplayer'
    imgCmdList = ["sudo","fbi","--once","-noverbose","-T","2"]
    files = os.listdir(mediaPath)
    files.sort()
    for file in files:
        # check file extension
        if isImage(file) and playerState == PLAYER_STARTED:
            # process image file
            curImgCmd = imgCmdList[:]
            curImgCmd.append(mediaPath + file)
            #subProc = subprocess.Popen(curImgCmd)
            # sleep while image is shown, append a second for loading time
            print "Showing image " + file + " for " + str(config['image_interval']) + " seconds"
            time.sleep(config['image_interval'] + 2)
            subProc.kill()
            subProc.wait()
        elif isVideo(file):
            playVideo(file)

def processAllFiles():
    print "Processing all files."
    if config['group_filetypes']:
        processImagesOnce()
        processVideosOnce()
        while config['repeat'] and playerState == PLAYER_STARTED:
            # check config for changes
            reloadConfig()
            processImagesOnce()
            processVideosOnce()
    else:
        processAllFilesOnce()
        while config['repeat'] and playerState == PLAYER_STARTED:
            # check config for changes
            reloadConfig()
            processAllFilesOnce()
    stop()
    

def processMediaFiles():
    print "Checking config on files to process:"
    print config
    if config['image_enabled'] and config['video_enabled']:
        processAllFiles()
    elif config['image_enabled']:
        processImagesOnly()
    elif config['video_enabled']:
        processVideosOnly()


def reloadConfig():
    global config
    config = configtool.readConfig()

def play():
    reloadConfig()
    global playerState
    playerState = PLAYER_STARTED

    # media file processing has to be done in a separate thread to not block udp server etc.
    media_thread = threading.Thread(target=processMediaFiles)
    media_thread.daemon = True
    media_thread.start()
    print "Mediaplayer running in thread: ", media_thread.name


def stop():
    global playerState, lock
    if playerState == PLAYER_STARTED:
        playerState == PLAYER_STOPPED
        # check for fbi and omxplayer processes and terminate them
        processtool.killProcesses('fbi')
        # stop omx player instance if running
        subprocess.call([cwd + '/scripts/quitplay.sh'])
        processtool.killProcesses('omxplayer')

    