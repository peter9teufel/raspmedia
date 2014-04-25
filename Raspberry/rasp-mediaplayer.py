#! /usr/bin/env python

# libraries
import os, sys, subprocess, time, threading

# hide console text of local tty0 on hdmi
os.system('sudo setterm -foreground black -clear >/dev/tty1')

# own modules and packages
from packages import rmconfig, rmmedia, rmutil, rmnetwork
from packages.rmnetwork import udpserver

def shellquote(s):
    return "'" +  s.replace("'", "'\\''") + "'"

def reloadConfig():
	global config
	if rmconfig.configtool.configFileAvailable():
		print "Reading config file..."
		config = rmconfig.configtool.readConfig()

def startMediaPlayer():
	# set config and path for player and start it
	rmmedia.mediaplayer.setMediaPath(mediaPath)
	if config['autoplay']:
		rmmedia.mediaplayer.play()

def startUdpServer():
	udpserver.start()

# startup image
# subprocess.call(["sudo","fbi","-a", "--once","-noverbose","-T","2", "./raspmedia.jpg"])

config = rmconfig.configtool.initConfig()
reloadConfig()

# default media path
mediaPath = os.getcwd() + '/media/'
print "Media Path: " + mediaPath

startMediaPlayer()
startUdpServer()


# simple CLI to modify and quit program when debugging
time.sleep(0.5)
print ""
print ""
print "Loading CLI....."
time.sleep(0.5)
print ""
print ""
print "Type commands any time -->"
print "-- \"start\" to start the UDP server"
print "-- \"stop\" to stop and close the UDP server"
print "-- \"quit\" to exit the program"

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