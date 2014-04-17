#! /usr/bin/env python

import os
import re
import subprocess
import time
import configtool

def shellquote(s):
    return "'" +  s.replace("'", "'\\''") + "'"

cwd = os.getcwd();
mediaPath = cwd + '/media/';

config = configtool.initConfig();
print config;
if configtool.configFileAvailable():
	config = configtool.readConfig(config);

print config;