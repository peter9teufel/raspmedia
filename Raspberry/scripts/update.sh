#!/bin/sh

# stop all player processes
echo 'Stopping player...'
sudo killall python fbi omxplayer mplayer
sleep 1
echo 'Done!'

echo 'Updating files...'
cd /home/pi/raspmedia
git pull origin master

echo 'Done! Rebooting player now...'
sudo reboot

exit
