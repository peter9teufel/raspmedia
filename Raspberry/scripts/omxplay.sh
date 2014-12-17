#!/bin/sh
# clean up command input
sudo rm /tmp/cmd
# create new command input file
sudo touch /tmp/cmd

# -o for audio output selection, -b to blackout screen, --vol amp in millibel
sudo omxplayer -b -o both $1 --vol 25 < /tmp/cmd
# echo child terminated
exit