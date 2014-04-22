#! /usr/bin/env python

import os, sys

def killProcesses(filter):
    info = os.popen("ps aux | grep '" + filter + "'").read();
    print info;
    infoFields = str(info).split();
    print infoFields;
    kill = False;
    savePID = False;
    pid = 0;
    fbiFound = False;
    for elem in infoFields:
        if kill:
            print "Killing process with PID " + str(pid);
            os.system("sudo kill " + str(pid));
            kill = False;
            pid = 0;
        else:
            if elem == 'root':
                savePID = True;
            elif elem == 'fbi':
                fbiFound = True;
            elif savePID:
                pid = int(elem);
                savePID = False;
            elif fbiFound:
                if elem == '--once' or elem == '-noverbose':
                    kill = True;
                fbiFound = False;


# DEBUG call
if len(sys.argv) > 1:
    killProcesses(sys.argv[1]);
