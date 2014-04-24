#! /usr/bin/env python

import os, threading, time, subprocess, re
from packages.rmutil import processtool
from packages.rmconfig import configtool
from constants import *

playerState = PLAYER_STOPPED
cwd = os.getcwd()

class MediaPlayer(threading.Thread):
    def __init__(self):
        global playerState
        self._stopevent = threading.Event()
        playerState = PLAYER_STOPPED
        print "INIT PLAYER STATE SET DONE!"
        threading.Thread.__init__(self, name="MediaPlayer_Thread")

    def run(self):
        global playerState
        print ":::::MEDIAPLAYER THREAD RUN METHOD STARTED:::::"
        while True:
            # wait until the player flag is set to STARTED
            while playerState == PLAYER_STOPPED:
                time.sleep(0.5)
            # remove raspmedia image process
            processtool.killProcesses('fbi')

            #reload config and process media files
            self.reloadConfig()
            playerState = PLAYER_STARTED
            self.processMediaFiles()
            time.sleep(1)
            self.showRaspMediaImage()

    def showRaspMediaImage(self):
        global cwd
        cmdList = ['sudo','fbi','-noverbose','-T','2', cwd + '/raspmedia.jpg']
        subprocess.call(cmdList)

    def setMediaPath(self, mediaPath):
        self.mediaPath = mediaPath

    def processImagesOnce(self):
        global playerState
        imgCmdList = ["sudo","fbi","-noverbose", "--once", "-t", str(self.config['image_interval']), "-blend", "400", "-T","2"]
        numImg = 0
        files = os.listdir(self.mediaPath)
        files.sort()
        for file in files:
            # check file extension
            if isImage(file):
                # process image file
                imgCmdList.append(self.mediaPath + file)
                numImg += 1
        print "Image command to call:"
        print imgCmdList
        subprocess.call(imgCmdList)

        i = 0
        while i < numImg and  playerState == PLAYER_STARTED:
            duration = (self.config['image_interval'] + 2)
            time.sleep(duration)
            i += 1

    def fbiImageLoop(self):
        global playerState
        imgCmdList = ["sudo","fbi","-noverbose", "-t", str(self.config['image_interval']), "-blend", "400", "-T","2"]
        numImg = 0
        for file in os.listdir(self.mediaPath):
            # check file extension
            if isImage(file):
                # process image file
                imgCmdList.append(self.mediaPath + file)
                numImg += 1
        print "Image command to call:"
        print imgCmdList
        subprocess.call(imgCmdList)
        # wait in loop as fbi command does not block and check for config changes
        while self.config['repeat'] and playerState == PLAYER_STARTED:
            # estimate duration of one loop of all images
            duration = numImg * (self.config['image_interval'] + 2) + 1
            time.sleep(duration)
            # check for config changes after approximately each loop
            self.reloadConfig()


    def processImagesOnly(self):
        global playerState
        print "Processing only images."
        if self.config['repeat']:
            self.fbiImageLoop()
        else:
            self.processImagesOnce()

    def processVideosOnce(self):
        global playerState
        for file in os.listdir(self.mediaPath):
            if playerState == PLAYER_STARTED:
                if isVideo(file):
                    self.playVideo(file)

    def processVideosOnly(self):
        global playerState
        print "Processing only videos."
        self.processVideosOnce()
        while self.config['repeat'] and playerState == PLAYER_STARTED:
            # check for config changes
            self.reloadConfig()
            self.processVideosOnce()

    def playVideo(self,file):
        global playerState
        # process video file -> omxplay will block until its done
        print "Status PLAYER_STARTED: ", playerState == PLAYER_STARTED
        if playerState == PLAYER_STARTED:
            print "Starting video file " + file
            subprocess.call([cwd + '/scripts/omxplay.sh', self.mediaPath + file])


    def processAllFilesOnce(self):
        global playerState
        vidCommand = 'sudo omxplayer'
        imgCmdList = ["sudo","fbi","--once","-noverbose","-T","2"]
        files = os.listdir(self.mediaPath)
        files.sort()
        for file in files:
            # check file extension
            if isImage(file) and playerState == PLAYER_STARTED:
                # process image file
                curImgCmd = imgCmdList[:]
                curImgCmd.append(self.mediaPath + file)
                subProc = subprocess.Popen(curImgCmd)
                # sleep while image is shown, append a second for loading time
                print "Showing image " + file + " for " + str(self.config['image_interval']) + " seconds"
                time.sleep(self.config['image_interval'] + 2)
                subProc.kill()
                subProc.wait()
            elif isVideo(file):
                self.playVideo(file)

    def processAllFiles(self):
        global playerState
        print "Processing all files."
        if self.config['group_filetypes']:
            self.processImagesOnce()
            self.processVideosOnce()
            while self.config['repeat'] and playerState == PLAYER_STARTED:
                # check config for changes
                self.reloadConfig()
                self.processImagesOnce()
                self.processVideosOnce()
        else:
            self.processAllFilesOnce()
            while self.config['repeat'] and playerState == PLAYER_STARTED:
                # check config for changes
                self.reloadConfig()
                self.processAllFilesOnce()
        

    def processMediaFiles(self):
        global playerState
        print "Checking config on files to process:"
        print self.config
        if self.config['image_enabled'] and self.config['video_enabled']:
            self.processAllFiles()
        elif self.config['image_enabled']:
            self.processImagesOnly()
        elif self.config['video_enabled']:
            self.processVideosOnly()

        # set player state to stopped as processing is done at this point
        playerState = PLAYER_STOPPED

    def reloadConfig(self):
        self.config = configtool.readConfig()



def getMediaFileList():
    files = []
    for file in os.listdir(mediaPath):
        if isImage(file) or isVideo(file):
            files.append(file)
    return files

def setMediaPath(curMediaPath):
    global mp_thread
    mp_thread.mediaPath = curMediaPath

def isImage(filename):
    supportedExtensions = ('.jpg', '.jpeg', '.JPG', '.JPEG', '.png', '.PNG')
    return filename.endswith((supportedExtensions))

def isVideo(filename):
    supportedExtensions = ('.mp4', '.m4v', '.mpeg', '.mpeg1', '.mpeg4')
    return filename.endswith((supportedExtensions))

def play():
    global playerState
    playerState = PLAYER_STARTED
    #global mp_thread
    #mp_thread.playerState = PLAYER_STARTED
    print "Mediaplayer running in thread: ", mp_thread.name


def stop():
    global mp_thread, lock
    # check for fbi and omxplayer processes and terminate them
    processtool.killProcesses('fbi')
    # stop omx player instance if running
    subprocess.call([cwd + '/scripts/quitplay.sh'])
    processtool.killProcesses('omxplayer')

def main():
    global cwd, mp_thread
    print "PLAYER CWD: " + cwd
    mp_thread = MediaPlayer()
    mp_thread.daemon = True
    # media file processing in separate thread --> started here and controlled via flag
    mp_thread.start()

main()