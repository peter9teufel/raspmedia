#RaspMedia Player for Raspberry Pi#

##Introduction##
RaspMedia is a standalone mediaplayer for the Raspberry Pi, intended to be used for digital signage. It provides image and video playback as a complete standalone solution and is fully configurable over the network using the enclosed Desktop applications.

###Features###
RaspMedia Player provides digital signage using image slideshows, videos or a combination of both. All media files can be easily copied to the player using the RaspMedia Control Desktop application. A second desktop application called *RaspMedia Copy Tool* (only available for Windows by now) allows an even more easy way to send mediafiles (currently only images with Copy Tool) to the RaspMedia Player, see description below.
The RaspMedia Player is intended as a complete standalone digital signage player. All configuration and media copying can be done over the network without the need to directly access the player, which makes it suitable for screens with less accessibility (e.g. outdoor cabinets etc.).
The RaspMedia Control Desktop Application needs no further configuration, it automatically detects all players in the local network within seconds.
The RaspMedia Player currently has to be connected via Ethernet. Future steps will include WiFi settings that can be done in the Desktop Application while connected via Ethernet to allow further access, configuration and data manipulation on the player over WiFi.

##Installation##
Setting up a RaspMedia player is easy, the complete installation on the raspberry pi is done using a installation script, the desktop software is written in python and can be simply compiled to an executable with pyinstaller using the provided *.spec file.

###Installation Raspberry Pi###
To prepare a fresh Raspberry Pi Raspbian setup you can run prepare_raspbian.sh which will prompt you for a new user password, set the gpu memory split and expand the filesystem.
  * Login on your Raspberry Pi locally or over SSH
  * Ensure that your Raspberry Pi is connected to the internet
  * Download the preparation script by calling:
  * `wget https://raw.githubusercontent.com/peter9teufel/raspmedia/master/prepare_raspbian.sh`
  * Make the preparation script executable with `sudo chmod +x ./prepare_raspbian.sh`
  * Start installation with `sudo ./prepare_raspbian.sh`

As the script has to modify system parts like memory split, filesystem extension etc. it has to be called with root rights using sudo.
When done the script launches raspi-config in case you want to modify more (e.g. time zone), otherwise simply choose finish in raspi-config and let the raspberry reboot. The preparation script automatically downloads the installation script and launches it when the reboot is done.
The installation script will install all required packages, load the up-to-date RaspMedia sources from the repo and setup the autostart of the RaspMedia application. The installation script has been tested on a clean Raspian Installation (version from 2014-06-20).
When the install script has finished the Raspberry Pi will reboot and directly launch the RaspMedia mediaplayer.
Preparation- and installation scripts are removed when the installation is done, the RaspMedia player is now ready for use

####MPEG Video decoding####
To be able to use RaspMedia with MPEG2 encoded video files you need to obtain a MPEG License for your Raspberry Pi. The MPEG License is bound to the serial number of a Raspberry Pi and thus can not be provided in advance here.

You can get your MPEG2 license at http://www.raspberrypi.com/mpeg-2-license-key/ for a few bucks.
MP4 videos may work well without obtaining a license, you may try your files before.

###Installation Desktop###
The repository also holds two desktop applications to be used with RaspMedia Player:
   * RaspMedia Control
   * RaspMedia Copy Tool

To use the desktop applications you have several ways:
  * Execute the main python script (needs all required packages to be installed locally)
  * Compile the application using pyinstaller and the provided *.spec files (needs all required packages to be installed locally)
  * Get a compiled executable for Mac (*.app) or Windows (32bit or 64bit) by requesting it directly from me. A site with up to date executables for free download will follow in the future.

As the desktop applications are one-file-executables that have all necessary python sources packed they need no further installation. Simply copy/paste them on your PC/Mac and execute them.

####Security and Firewall####
Mac prevents the execution from applications that have not been signed by a registered Mac developer. Therefor you need to go to System settings --> security and confirm that you want to open the app allthough it is from a unregistered developer. This has only to be done once.
Also make sure that your firewall (if you use one) does not block the program. While testing the 32bit version on Windows it was necessary to add an exceptional case in the firewall settings for the executable to be able to access the RaspMedia Player over the network.

####RaspMedia Control####
#####Main Window#####
RaspMedia Control allows you to fully configure and setup your RaspMedia Players. On startup the application searches for players in your local network and creates a tab for each player.
![RaspMedia Control Main Window](/Screenshots/rmc_main.png)

The main window offers information on the player (name, IP) and basic controls (Play, Stop, Reboot) at the top, by clicking identify the corresponding player will show a test image with the player name so you can identify each player and give it a appropriate name when setting up multiple players at one time.
Right underneath you can find a simple file explorer to search for images on your hard drive which you'd like to send to the player. You can send a single image by double clicking it and approving the dialog or by selecting multiple images, right click and select "Send to player".
The bottom list is the list of files you currently have on your RaspMedia Player. You can delete single files by double clicking them or again select multiple files, right click them and select "Delete from player".
If at any time you think the remote list is not up to date (which can occur due to network performance etc.) you can click "Refresh remote filelist" to update the list of files from your player.
#####Player Settings#####
From the *File* menu you can access the *Player Settings* to configure some playback options.
![RaspMedia Player Settings](/Screenshots/rmc_player_settings.png)

The settings are self explanatory, you can enable image and video playback, select if the player should automatically start playback after booting, set the interval for image slideshows and give the player a name.
The settings also enable you to update the player to the newest version (needs internet connection).
####RaspMedia Copy Tool####
The RaspMedia Copy Tool is currently compatible with Microsoft Windows and Mac OS X. The main purpose of this application is to provide an easy way to bring media files on a RaspMedia Player for *technophobic* users.
When starting the application it searches all players in the local network. When done so it prompts to connect a USB Stick with the media files to copy to the PC.
![RaspMedia Copy Tool USB Prompt](/Screenshots/rmcopy_usb.png)

All media files (currently only images) on the root directory of the USB Stick will be copied, the order of the images used on the player depends on their filenames. When the USB stick is found the main window appears, listing the number of players found on the network, the drive letter of the USB stick (to be compared in Explorer if you like) and a scrollable preview of all images found on the USB drive that will be copied to the player(s). A checkbox allows to decide whether the images that are currently on the player should be deleted or not. Images with identical names will be overwritten.
![RaspMedia Copy Tool Main Window](/Screenshots/rmcopy_main.png)

The application allows you to send the images to all players or to a specific player. Additionally you have the possibility to start the players synchronously.

In addition to the copy feature the RaspMedia Copy Tool provides the same *Player Settings* functionality as RaspMedia Control does via the *File* menu.

###Language support###
The desktop applications *RaspMedia Control* and *RaspMedia Copy Tool* are currently available in english and german using the string files in the *lang* package (strings_de.py, strings_en.py). The language is selected according to the default locale of the system the application is started. If the language code of the default locale is unknown, english is selected as the default language.
Additional languages can be added by translating the strings file for the new language and add the appropriate language code in the part where the *Localizer* (see package *lang*) checks the code of the default locale.

##License##
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
