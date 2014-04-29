#! /usr/bin/env python

import os, re, subprocess, time, json

cwd = os.getcwd()
configFile = cwd + '/main.conf'
config = {}

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

def setConfigValue(key, value):
	global config
	if is_number(value):
		value = int(value)
	config[key] = value
	writeConfigFile()

def writeConfigFile():
	global config
	f = open(configFile, 'w')
	json.dump(config, f)
	f.close()
	print "Config file updated!"

def readConfig():
	global config
	#check if config file exists
	if os.path.isfile(configFile):
		print "Config file found!"
		with open(configFile) as conf:
			config = json.load(conf)
			conf.close()
			#configContent = conf.readlines()
			
		#for i in range(len(configContent)):
		#	curConf = (configContent[i]).rstrip('\n')
		#	if not curConf.startswith("#"):
		#		params = re.split(':', curConf)
		#		if len(params) == 2:
		#			key = params[0]
		#			value = params[1]
		#			# print "KEY: " + key + " - VALUE: " + value
		#			setConfigValue(key, value)
	else:
		print "No config file found!"
	return config

def configFileAvailable():
	print "Checking config file path: " + configFile
	if os.path.isfile(configFile):
		return True
	else:
		return False

