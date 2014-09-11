#! /usr/bin/env python

# libraries
import os, sys, subprocess, time, threading

# own modules and packages
from packages import rmconfig, rmmedia, rmutil, rmnetwork
from packages.rmnetwork import udpserver, tcpfilesocket, udpbroadcaster, messages, GroupManager
from constants import *

config = {}

def shellquote(s):
    return "'" +  s.replace("'", "'\\''") + "'"

def startMediaPlayer():
	# set config and path for player and start it
    # rmmedia.mediaplayer.main()
    global config
    config = rmconfig.configtool.readConfig()
    rmmedia.mediaplayer.setMediaPath(mediaPath)
    rmmedia.mediaplayer.identify = False
    if config['autoplay']:
        rmmedia.mediaplayer.play()

def startUdpServer():
	udpserver.start()


def openFileSocket():
    tcpfilesocket.openFileSocket()

def main():
    global config, groupConfig, mediaPath
    config = rmconfig.configtool.initConfig()

    # default media path
    mediaPath = os.getcwd() + '/media/'
    #print "Media Path: " + mediaPath

    print "Launching player..."

    # hide console text of local tty0 on hdmi
    os.system('sudo setterm -foreground black -clear >/dev/tty1')

    startUdpServer()
    openFileSocket()
    startMediaPlayer()

    # send boot complete broadcast
    msgData = messages.getMessage(PLAYER_BOOT_COMPLETE)
    udpbroadcaster.sendBroadcast(msgData, True)

    # initialize group manager with group configuration
    groupConfig = rmconfig.configtool.readGroupConfig()
    GroupManager.InitGroupManager(groupConfig)
    GroupManager.Schedule()


    # simple CLI to modify and quit program when debugging
    print ""
    print ""
    print "Type commands any time -->"
    print "-- \"start\" to start the UDP server"
    print "-- \"stop\" to stop and close the UDP server"
    print "-- \"quit\" to exit the program"
    print ""
    print ""

    running = True
    while running:
        cmd = raw_input("")
        if(cmd == "start"):
            udpserver.start()
        elif(cmd == "stop"):
            udpserver.stop()
        elif(cmd == "quit"):
        	running = False
        else:
        	print "Unknown command: ", cmd

    # bring back console text on tty0 on hdmi
    os.system('sudo setterm -foreground white -clear >/dev/tty1')
    udpserver.stop()
    rmutil.processtool.killProcesses('fbi')
    # startup image
    # subprocess.call(["sudo","fbi","--once","-a","-noverbose","-T","2", "./raspmedia.jpg"])

if __name__ == '__main__':
    print ""
    print ":::::::::::::::::::::::::::::::::::::::::::::::::"
    print ":::::::::: WELCOME TO RASPMEDIA PLAYER ::::::::::"
    print ":::::::::::::::::::::::::::::::::::::::::::::::::"
    print ""
    main()
