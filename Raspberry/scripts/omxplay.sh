#!/bin/sh
# clean up command input
sudo rm /tmp/cmd
# create new command input file
sudo touch /tmp/cmd

sudo omxplayer -o hdmi -r $1 < /tmp/cmd
# echo child terminated
exit