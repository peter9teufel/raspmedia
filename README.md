RaspMedia Mediaplayer for Raspberry Pi
=========
Introduction
=====
RaspMedia is a standalone mediaplayer for the Raspberry Pi, intended to be used for digital signage. It provides image and video playback as a complete standalone solution is fully configurable over the network using the enclosed Desktop applications.
Installation Raspberry Pi
=====
To prepare a fresh raspberry pi Raspian setup you can run prepare_raspian.sh which will prompt you for a new user password, set the gpu memory split and expand the filesystem. When done the script launches raspi-config in case you want to modify more (e.g. time zone), otherwise simply choose finish in raspi-config and let the raspberry reboot. The preparation script automatically downloads the installation script and launches it when the reboot is done.
The installation script will install all required packages, load the up-to-date RaspMedia sources from the repo and setup the autostart of the RaspMedia application. The installation script has been tested on a clean Raspian Installation (version from 2014-06-20).
When the install script has finished the Raspberry Pi will reboot and directly launch the RaspMedia mediaplayer.
Preparation- and installation scripts are removed when the installation is done, the RaspMedia player is now ready for use
Installation Desktop
=====
The repository also holds two desktop applications to be used with RaspMedia Player:
* RaspMedia Control
* RaspMedia Copy Tool
RaspMedia Control
=====
Explanation of RaspMediaControl.
RaspMedia Copy Tool
===
Explanation of Copy Tool
Future work
===
License
===
Copyright 2014 Peter Neunteufel

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
