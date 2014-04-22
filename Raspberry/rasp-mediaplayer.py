#! /usr/bin/env python

# libraries
import os, sys, subprocess, time

# own modules and packages
import rmconfig, rmmedia, rmutil
#from .rmconfig import configtool
#from .rmmedia import mediaplayer
#from .rmutil import processtool

def shellquote(s):
    return "'" +  s.replace("'", "'\\''") + "'"


# startup image
# subprocess.call(["sudo","fbi","-a", "--once","-noverbose","-T","2", "./raspmedia.jpg"]);

config = rmconfig.configtool.initConfig();
print config;
if rmconfig.configtool.configFileAvailable():
	print "Reading config file...";
	config = rmconfig.configtool.readConfig(config);

print config;

mediaPath = os.getcwd() + '/media/';
print "Media Path: " + mediaPath;

# set config and path for player and start it
rmmedia.mediaplayer.init(config, mediaPath);

rmmedia.mediaplayer.play();
# startup image
# subprocess.call(["sudo","fbi","--once","-a","-noverbose","-T","2", "./raspmedia.jpg"]);