#! /usr/bin/env python

import os, sys

def killProcesses(filter):
    if filter == 'fbi':
        killFbiProcesses()
    else:
        info = os.popen("ps aux | grep '" + filter + "'").read();
        print info;
        infoFields = str(info).split();
        print infoFields;
        kill = False;
        savePID = False;
        pid = 0;
        found = False;
        for elem in infoFields:
            if kill:
                print "Killing process with PID " + str(pid);
                os.system("sudo kill " + str(pid));
                kill = False;
                pid = 0;
            else:
                if elem == 'root':
                    savePID = True;
                elif filter in elem:
                    found = True;
                elif savePID:
                    pid = int(elem);
                    savePID = False;
                elif found:
                    kill = True;
                    found = False;


def killFbiProcesses():
    filter = 'fbi'
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
