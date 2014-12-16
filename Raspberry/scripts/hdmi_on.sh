#!/bin/bash
groups=(UNKNOWN CEA DMT)
group=$(vcgencmd get_config hdmi_group)
mode=$(vcgencmd get_config hdmi_mode)
newGroup="${group#*=}"
newMode="${mode#*=}"
groupName=${groups[$newGroup]}
tvservice --explicit=$groupName" "$newMode" HDMI"
