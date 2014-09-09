#! /usr/bin/env python

import os, re, subprocess, time, json

cwd = os.getcwd()
mainConfigFile = cwd + '/main.conf'
groupConfigFile = cwd + '/group.conf'

config = {}
groupConfig = {}

def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def initConfig():
	global config
	config = {}
	config["userMediaPath"] = ""
	config["image_interval"] = 4
	config["image_blend_interval"] = 300
	config["video_enabled"] = 1
	config["image_enabled"] = 1
	config["autoplay"] = 1
	config["group_filetypes"] = 1
	config["shuffle"] = 0
	config["repeat"] = 1
	config["userPlaylist"] = ""
	return config

def initGroupConfig():
    global groupConfig
    groupConfig["group"] = None
    groupConfig["group_master"] = False
    groupConfig["group_master_name"] = None
    groupConfig["actions"] = []

def resetGroupConfig():
    initGroupConfig()
    writeGroupConfigFile()

def setConfigValue(key, value):
	global config
	if is_number(value):
		value = int(value)
	config[key] = value
	writeConfigFile()

def setGroupConfigValue(key, value):
    global groupConfig
    if is_number(value):
        value = int(value)
    groupConfig[key] = value
    writeGroupConfigFile()

def addGroupAction(action):
    global groupConfig
    groupConfig = readGroupConfig()
    groupConfig["actions"].append(action)
    writeGroupConfigFile()

def writeConfigFile():
	global config
	f = open(mainConfigFile, 'w')
	json.dump(config, f)
	f.close()
	print "Config file updated!"

def writeGroupConfigFile():
    global groupConfig
    f = open(groupConfigFile, 'w')
    json.dump(groupConfig, f)
    f.close()
    print "Group config file updated!"

def readConfig():
	global config
	#check if config file exists
	if os.path.isfile(mainConfigFile):
		print "Config file found!"
		with open(mainConfigFile) as conf:
			config = json.load(conf)
			conf.close()
	else:
		print "No config file found!"
	return config

def readGroupConfig():
    global groupConfig
    print "Checking group config..."
    if os.path.isfile(groupConfigFile):
        with open(groupConfigFile) as group:
            groupConfig = json.load(group)
            group.close()
    else:
        initGroupConfig()
    return groupConfig


def configFileAvailable():
	print "Checking config file path: " + mainConfigFile
	if os.path.isfile(mainConfigFile):
		return True
	else:
		return False
