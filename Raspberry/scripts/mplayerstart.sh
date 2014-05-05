#!/bin/sh
# clean up command input
sudo rm /tmp/cmd
# create new command input file
sudo touch /tmp/cmd

sudo mplayer -fs -zoom "$@" < /tmp/cmd
# echo child terminated
exit