#!/bin/sh

###play the requested file taking commands from /tmp/omxcmd
### remove >/dev/null to see stdout from omxplayer
# echo $CC $SS $FF
sudo omxplayer -o hdmi -r $1
# echo child terminated
exit