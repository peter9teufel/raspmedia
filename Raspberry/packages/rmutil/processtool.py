#! /usr/bin/env python

import os

def killProcesses(filter):
    os.system("sudo killall " + filter + " > /dev/null")
    


def killFbiProcesses():
    killProcesses('fbi')

