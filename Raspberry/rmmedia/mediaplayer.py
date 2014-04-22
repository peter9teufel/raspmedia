#! /usr/bin/env python

import os, time, subprocess, re
from rmutil import processtool
from rmconfig import configtool

cwd = os.getcwd()
mediaPath = ''
config = configtool.config

def init(curMediaPath):
    global mediaPath
    mediaPath = curMediaPath

def isImage(filename):
    supportedExtensions = ('.jpg', '.jpeg', '.JPG', '.JPEG', '.png', '.PNG')
    return filename.endswith((supportedExtensions))

def isVideo(filename):
    supportedExtensions = ('.mp4', '.m4v', '.mpeg', '.mpeg1', '.mpeg4')
    return filename.endswith((supportedExtensions))

def processImagesOnce():
    imgCmdList = ["sudo","fbi","-noverbose", "--once", "-t", str(config['image_interval']), "-blend", "300", "-T","2"]
    numImg = 0
    for file in os.listdir(mediaPath):
        # check file extension
        if isImage(file):
            # process image file
            imgCmdList.append(mediaPath + file)
            numImg = numImg + 1
    print "Image command to call:"
    print imgCmdList
    #subprocess.call(imgCmdList)
    #duration = numImg + (config['image_interval'] + 2) + 1
    #time.sleep(duration)

def processImagesOnly():
    print "Processing only images."
    processImagesOnce()
    while config['repeat']:
        processImagesOnce()

def processVideosOnce():
    for file in os.listdir(mediaPath):
        if isVideo(file):
            # process video file -> omxplay will block until its done
            print "Starting video file " + file
            #subprocess.call([cwd + 'scripts/omxplay.sh', mediaPath + file])

def processVideosOnly():
    print "Processing only videos."
    processVideosOnce()
    while config['repeat']:
        processVideosOnce()

def processAllFilesOnce():
    vidCommand = 'sudo omxplayer'
    imgCmdList = ["sudo","fbi","--once","-noverbose","-T","2"]
    for file in os.listdir(mediaPath):
        # check file extension
        if isImage(file):
            # process image file
            curImgCmd = imgCmdList[:]
            curImgCmd.append(mediaPath + file)
            #subProc = subprocess.Popen(curImgCmd)
            # sleep while image is shown, append a second for loading time
            print "Showing image " + file + " for " + str(config['image_interval']) + " seconds"
            #time.sleep(config['image_interval'] + 2)
            #subProc.kill()
            #subProc.wait()
        elif isVideo(file):
            # process video file -> omxplay will block until its done
            print "Starting video file " + file
            #subprocess.call([cwd + '/omxplay.sh', mediaPath + file])

def processAllFiles():
    print "Processing all files."
    processAllFilesOnce()
    while config['repeat']:
        processAllFilesOnce()
    

def processMediaFiles():
    print "Checking config on files to process:"
    print config
    if config['image_enabled'] and config['video_enabled']:
        processAllFiles()
    elif config['image_enabled']:
        processImagesOnly()
    elif config['video_enabled']:
        processVideosOnly()


def play():
    # first process of mediafiles
    processMediaFiles()
    # check for fbi processes when done
    processtool.killProcesses('fbi')
    #while config['repeat']:
    #    processMediaFiles()
  
    