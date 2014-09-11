#! /usr/bin/env python

import os, re, subprocess, time, json, ast

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
    if configFileAvailable():
        # config file available
        config = readConfig()
    else:
        # no config file available --> init
    	config = {}
    	config["userMediaPath"] = ""
    	config["image_interval"] = 4
    	config["image_blend_interval"] = 550
    	config["video_enabled"] = 0
    	config["image_enabled"] = 1
    	config["autoplay"] = 1
    	config["group_filetypes"] = 1
    	config["shuffle"] = 0
    	config["repeat"] = 1
    	config["userPlaylist"] = ""
        writeConfigFile()
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
    if __actionIndex(action) == -1:
        # action not in list --> append and save
        groupConfig["actions"].append(action)
        writeGroupConfigFile()

def __actionIndex(action):
    ind = -1
    cnt = 0
    # convert to dict in case it is still a string
    action = __toDict(action)
    action = __sortDict(action)
    for a in groupConfig['actions']:
        a = __toDict(a)
        a = __sortDict(a)
        if cmp(a, action) == 0:
            ind = cnt
        cnt += 1
    return ind

def __toDict(data):
    try:
        dict = ast.literal_eval(data)
        data = dict
    except:
        pass
    return data

def deleteGroupAction(action):
    global groupConfig
    readGroupConfig()
    ind = __actionIndex(action)
    if not ind == -1:
        del groupConfig['actions'][ind]
    writeGroupConfigFile()

def __sortDict(dict):
    sDict = {}
    for key in sorted(dict):
        sDict[key] = dict[key]
    return sDict

def writeConfigFile():
	global config
	f = open(mainConfigFile, 'w')
	json.dump(config, f)
	f.close()

def writeGroupConfigFile():
    global groupConfig
    f = open(groupConfigFile, 'w')
    json.dump(groupConfig, f)
    f.close()

def readConfig():
	global config
	#check if config file exists
	if os.path.isfile(mainConfigFile):
		with open(mainConfigFile) as conf:
			config = json.load(conf)
			conf.close()
	else:
		print "No config file found!"
	return config

def readGroupConfig():
    global groupConfig
    if os.path.isfile(groupConfigFile):
        with open(groupConfigFile) as group:
            groupConfig = json.load(group)
            group.close()
    else:
        initGroupConfig()
    return groupConfig


def configFileAvailable():
	if os.path.isfile(mainConfigFile):
		return True
	else:
		return False
