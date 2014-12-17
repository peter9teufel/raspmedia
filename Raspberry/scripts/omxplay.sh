#!/bin/sh
# clean up command input
#sudo rm /tmp/cmd
# create new command input file
#sudo touch /tmp/cmd

sudo omxplayer -o both $1
# echo child terminated
exit