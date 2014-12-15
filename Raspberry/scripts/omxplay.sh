#!/bin/sh
# clean up command input
sudo rm /tmp/cmd
# create new command input file
sudo touch /tmp/cmd

sudo omxplayer -o both $1 -vol 50 < /tmp/cmd
# echo child terminated
exit