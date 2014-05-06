#! /usr/bin/env python

import os

def killProcesses(filter):
    os.system("sudo killall " + filter)
    


def killFbiProcesses():
    killProcesses('fbi')

