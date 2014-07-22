#!/bin/sh
# Sets gpu memory to 128 MB
sudo echo "gpu_mem=128" >> /boot/config.txt;

# prompt for a new user password
passwd pi;

# download the raspmedia installation script and make it executable
cd /home/pi;
wget https://raw.githubusercontent.com/peter9teufel/raspmedia/master/install_raspmedia.sh;
sudo chmod +x install_raspmedia.sh;

#
#
# Resize the root filesystem of a newly flashed Raspbian image.
# Directly equivalent to the expand_rootfs section of raspi-config.
# No claims of originality are made.
#
# Run as root.  Expands the root file system.  After running this,
# reboot and give the resizefs-once script a few minutes to finish expanding the file system.
# Check the file system with 'df -h' once it has run and you should see a size
# close to the known size of your card.
#

  # Get the starting offset of the root partition
PART_START=$(parted /dev/mmcblk0 -ms unit s p | grep "^2" | cut -f 2 -d:)
[ "$PART_START" ] || return 1
# Return value will likely be error for fdisk as it fails to reload the
# partition table because the root fs is mounted
fdisk /dev/mmcblk0 <<EOF
p
d
2
n
p
2
$PART_START

p
w
EOF

# now set up an init.d script
cat <<\EOF > /etc/init.d/resize2fs_once &&
#!/bin/sh
### BEGIN INIT INFO
# Provides:          resize2fs_once
# Required-Start:
# Required-Stop:
# Default-Start: 2 3 4 5 S
# Default-Stop:
# Short-Description: Resize the root filesystem to fill partition
# Description:
### END INIT INFO

. /lib/lsb/init-functions

case "$1" in
  start)
    log_daemon_msg "Starting resize2fs_once" &&
    resize2fs /dev/mmcblk0p2 &&
    rm /etc/init.d/resize2fs_once &&
    update-rc.d resize2fs_once remove &&
    log_end_msg $?
    ;;
  *)
    echo "Usage: $0 start" >&2
    exit 3
    ;;
esac
EOF
chmod +x /etc/init.d/resize2fs_once &&
update-rc.d resize2fs_once defaults &&
  echo "Root partition has been resized. The filesystem will be enlarged after reboot"
sudo raspi-config .

echo "Setting automatic installation of RaspMedia on next reboot"
# modify rc.local to start raspmedia installation script at boot
sudo head -n -2 /etc/rc.local > /home/pi/rc.local.tmp;
sudo cat /home/pi/rc.local.tmp > /etc/rc.local;
sudo echo '' >> /etc/rc.local;
sudo echo '' >> /etc/rc.local;
sudo echo 'cd /home/pi/' >> /etc/rc.local;
sudo echo 'sudo ./install_raspmedia.sh' >> /etc/rc.local;
sudo echo 'exit 0' >> /etc/rc.local;
sudo rm /home/pi/rc.local.tmp;

echo "rc.local modified:";
echo /etc/rc.local;
echo "Rebooting now...";
sudo reboot;
