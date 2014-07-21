#! /usr/bin/env python

import os, platform, threading, time, subprocess, re
from packages.rmutil import processtool
from packages.rmconfig import configtool
from constants import *
from pyomxplayer import OMXPlayer
import ImageIdentifier

playerState = PLAYER_STOPPED
cwd = os.getcwd()
mediaPath = cwd + '/media/'
mp_thread = None
identifyFlag = False
previousState = None

class MediaPlayer(threading.Thread):
    def __init__(self):
        global playerState
        self.mediaPath = os.getcwd() + '/media/'
        self.runevent = threading.Event()
        self.identify_event = threading.Event()
        playerState = PLAYER_STOPPED
        threading.Thread.__init__(self, name="MediaPlayer_Thread")

    def run(self):
        global playerState, identifyFlag
        print ":::::MEDIAPLAYER THREAD RUN METHOD STARTED:::::"
        self.reloadConfig()

        # show player startup image for 3 seconds (+ loading time)
        self.showRaspMediaImage()
        time.sleep(5)

        # enter media player thread loop
        while True:
            # wait until the player flag is set to STARTED
            #while playerState == PLAYER_STOPPED:
            #    time.sleep(0.5)
            self.runevent.wait()
            # remove raspmedia image process
            processtool.killProcesses('fbi')

            if identifyFlag:
                self.showIdentifyImage()
                self.identify_event.wait()
                if playerState == PLAYER_STOPPED:
                    self.showRaspMediaImage()
            else:
                #reload config and process media files
                self.reloadConfig()
                playerState = PLAYER_STARTED
                self.processMediaFiles()
                time.sleep(0.5)
                self.showRaspMediaImage()

    def showRaspMediaImage(self):
        global cwd
        cmdList = ['sudo','fbi','-noverbose','-T','2', '-a', cwd + '/raspmedia.jpg']
        subprocess.call(cmdList)

    def showIdentifyImage(self):
        global cwd
        path = cwd
        if os.path.isfile(cwd + '/raspidentified.jpg'):
            path += '/raspidentified.jpg'
        else:
            path += '/raspidentify.jpg'
        cmdList = ['sudo','fbi','-noverbose','-T','2', '-a', path]
        subprocess.call(cmdList)

    def setMediaPath(self, mediaPath):
        self.mediaPath = mediaPath

    def processImagesOnce(self):
        global playerState
        imgInterval = str(self.config['image_interval'])
        blendInterval = str(self.config['image_blend_interval'] - 1)
        imgCmdList = ["sudo","fbi","-noverbose", "--once", "-readahead", "-t", imgInterval, '-a', "-blend", blendInterval, "-T","2"]
        numImg = 0
        files = self.allImages()
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
        wakes = 0
        duration = numImg * (self.config['image_interval'] + 1)
        while i < duration and  playerState == PLAYER_STARTED:
            time.sleep(1)
            i += 1
            wakes += 1
            if wakes > 10:
                print "Waking up and checking config...."
                # print "Seconds running: ",i
                # print "Calculated duration: ",duration
                # check config every 10 seconds
                self.reloadConfig()
                wakes = 0
        stop()

    def fbiImageLoop(self):
        global playerState
        imgInterval = str(self.config['image_interval'])
        blendInterval = str(self.config['image_blend_interval'])
        imgCmdList = ["sudo","fbi","-noverbose", "-readahead", "-t", imgInterval, '-a', "-blend", blendInterval, "-T","2"]
        numImg = 0
        files = self.allImages()
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
        wakes = 0
        # wait in loop as fbi command does not block and check for config changes
        while self.config['repeat'] and playerState == PLAYER_STARTED:
            time.sleep(1)
            wakes += 1
            if wakes > 10:
                # check for config changes every 10 seconds
                self.reloadConfig()
                wakes = 0


    def processImagesOnly(self):
        global playerState
        print "Processing only images."
        if self.config['repeat']:
            self.fbiImageLoop()
        else:
            self.processImagesOnce()

    def processVideosOnce(self):
        global playerState
        files = self.allVideos()
        files.sort()
        for file in files:
            if playerState == PLAYER_STARTED:
                if isVideo(file):
                    self.playVideo(file)

    def singleVideoLoop(self, filename):
        duration = self.getVideoDurationSeconds(filename)
        fullPath = self.mediaPath + filename
        print "VIDEO PATH: ", fullPath
        looper1 = OMXPlayer(fullPath, start_playback=True)
        looper2 = OMXPlayer(fullPath, start_playback=True)
        looper2.toggle_pause()
        looper1Active = True
        pos = 0
        while self.config['repeat'] and playerState == PLAYER_STARTED:
            if looper1Active:
                pos = looper1.position
            else:
                pos = looper2.position
            # print "Position: ", pos
            if pos > duration -2:
                print "TOGGLING LOOPERS..."
                # start other looper, wait 3 seconds and reload current looper for next round
                if looper1Active:
                    looper2.toggle_pause()
                    looper1.stop()
                    time.sleep(1)
                    looper1 = OMXPlayer(fullPath, start_playback=True)
                    looper1.toggle_pause()
                else:
                    looper1.toggle_pause()
                    looper2.stop()
                    time.sleep(1)
                    looper2 = OMXPlayer(fullPath, start_playback=True)
                    looper2.toggle_pause()
                looper1Active = not looper1Active
            time.sleep(0.1)
        if looper1:
            looper1.stop()
        if looper2:
            looper2.stop()

    def getVideoDurationSeconds(self, filename):
        proc = subprocess.Popen(['mplayer', '-vo', 'null', '-ao', 'null', '-frames', '0', '-identify', self.mediaPath + filename], stdout=subprocess.PIPE)
        output = proc.stdout.read()
        # print "Process Output: ", output
        ind = output.index('ID_LENGTH')
        start = ind + 10
        end = output.index('.',start)
        durStr = output[start:end]
        duration = int(durStr)
        print "VIDEO DURATION: ",duration
        return duration

    def videoLoop(self):
        videos = self.allVideos()
        if len(videos) == 1:
            self.singleVideoLoop(videos[0])
        else:
            while self.config['repeat'] and playerState == PLAYER_STARTED:
                # check for config changes
                self.reloadConfig()
                self.processVideosOnce()

    def processVideosOnly(self):
        global playerState
        print "Processing only videos."
        if self.config['repeat']:
            self.videoLoop()
        else:
            self.processVideosOnce()
        stop()


    def playVideo(self,file):
        global playerState
        # process video file -> omxplay will block until its done
        print "Status PLAYER_STARTED: ", playerState == PLAYER_STARTED
        if playerState == PLAYER_STARTED:
            # file = re.escape(file)
            print "Starting video file " + file
            # check if raspberry pi or ubuntu testing machine
            fullPath = self.mediaPath + file
            print "Full Path:"
            print fullPath
            if platform.system() == 'Linux' and platform.linux_distribution()[0] == 'Ubuntu':
                subprocess.call([cwd + '/scripts/mplayerstart.sh', fullPath])
            else:
                subprocess.call([cwd + '/scripts/omxplay.sh', self.mediaPath + file])


    def processAllFilesOnce(self):
        global playerState
        imgCmdList = ["sudo","fbi","--once","-noverbose","-readahead","-T","2"]
        files = self.allMediaFiles()
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
                time.sleep(self.config['image_interval'] + 2    )
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

    def allImages(self):
        images = []
        for file in os.listdir(self.mediaPath):
            if file.endswith((SUPPORTED_IMAGE_EXTENSIONS)):
                images.append(file)
        return images

    def allVideos(self):
        videos = []
        for file in os.listdir(self.mediaPath):
            if file.endswith((SUPPORTED_VIDEO_EXTENSIONS)):
                videos.append(file)
        return videos

    def allMediaFiles(self):
        files = []
        for file in os.listdir(self.mediaPath):
            if file.endswith((SUSUPPORTED_VIDEO_EXTENSIONS)) or file.endswith((SUPPORTED_IMAGE_EXTENSIONS)):
                files.append(file)
        return files

    def processMediaFiles(self):
        global playerState
        print "Checking config on files to process:"
        print self.config
        if self.config['image_enabled'] and self.config['video_enabled']:
            if len(self.allMediaFiles()) > 0:
                self.processAllFiles()
            else:
                stop()
        elif self.config['image_enabled']:
            if len(self.allImages()) > 0:
                self.processImagesOnly()
            else:
                stop()
        elif self.config['video_enabled']:
            if len(self.allVideos()) > 0:
                self.processVideosOnly()
            else:
                stop()

        # set player state to stopped as processing is done at this point
        playerState = PLAYER_STOPPED

    def reloadConfig(self):
        self.config = configtool.readConfig()



def getMediaFileList():
    global mediaPath
    files = []
    for file in os.listdir(mediaPath):
        if isImage(file) or isVideo(file):
            fileEnc = file.encode('utf-8')
            files.append(fileEnc)
    return files

def getImageFilelist():
    global mediaPath
    files = []
    for file in os.listdir(mediaPath):
        if isImage(file):
            fileEnc = file.encode('utf-8')
            files.append(fileEnc)
    return files

def setMediaPath(curMediaPath):
    global mp_thread, mediaPath
    mediaPath = curMediaPath
    mp_thread.mediaPath = curMediaPath

def deleteFiles(files):
    global mediaPath
    global playerState
    restart = False
    if playerState == PLAYER_STARTED:
        stop()
        restart = True
        time.sleep(1)

    path = mediaPath
    if not path.endswith('/'):
        path += "/"
    for file in files:
        fullPath = path + file
        if os.path.isfile(fullPath):
            os.remove(fullPath)

    if restart:
        play()
        time.sleep(1)

def isImage(filename):
    return filename.endswith((SUPPORTED_IMAGE_EXTENSIONS))

def isVideo(filename):
    return filename.endswith((SUPPORTED_VIDEO_EXTENSIONS))

def identifySelf():
    global identifyFlag, mp_thread, playerState, previousState
    previousState = playerState
    if playerState == PLAYER_STARTED:
        stop()
        time.sleep(0.5)
    identifyFlag = True
    config = configtool.readConfig()
    ImageIdentifier.IdentifyImage(config['player_name'])
    print "Image prepared..."
    mp_thread.identify_event.clear()
    play()

def identifyDone():
    global identifyFlag, mp_thread, previousState
    if previousState == PLAYER_STOPPED:
        stop()
    identifyFlag = False
    mp_thread.identify_event.set()

def play():
    global playerState
    playerState = PLAYER_STARTED
    global mp_thread

    # media file processing in separate thread
    if not mp_thread.isAlive():
        mp_thread.start()
    mp_thread.runevent.set()
    #global mp_thread
    #mp_thread.playerState = PLAYER_STARTED
    print "Mediaplayer running in thread: ", mp_thread.name


def stop():
    global mp_thread
    global playerState
    playerState = PLAYER_STOPPED
    mp_thread.runevent.clear()
    # check for fbi and omxplayer processes and terminate them
    processtool.killProcesses('fbi')
    # stop omx player instance if running
    subprocess.call([cwd + '/scripts/quitplay.sh'])
    processtool.killProcesses('omxplayer')

def main():
    global cwd, mp_thread, playerState
    print "PLAYER CWD: " + cwd
    if not mp_thread:
        mp_thread = MediaPlayer()
        mp_thread.daemon = True
    playerState = PLAYER_STOPPED
    mp_thread.start()

main()
