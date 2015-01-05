#RaspMedia Player for Raspberry Pi#

##Introduction##
RaspMedia is a standalone mediaplayer for the Raspberry Pi and the Banana Pi, intended to be used e.g. for digital signage. It provides image and video playback as a complete standalone solution and is fully configurable over the network using the enclosed Desktop applications.

###Features###
RaspMedia Player provides digital signage using image slideshows, videos or a combination of both. All media files can be easily copied to the player using the Desktop applications *RaspMedia Control*, *RaspMedia Copy Tool* or *RaspMedia Image Transfer*.

Furthermore it is possible to load a new set of mediafiles to a RaspMedia Player using an USB Stick. Simply create a folder called *raspmedia* in the root directory of a FAT32 formated USB Stick, put in your videos and/or images, plug the drive to your player and boot it up. The player will recognize the new mediafiles inside the *raspmedia* folder, copy them and configure the player according to the new files (enabling/disabling image and video processing).

The RaspMedia Player is intended as a complete standalone digital signage player. All configuration and media copying can be done over the network without the need to directly access the player, which makes it suitable for screens with less accessibility (e.g. outdoor cabinets etc.).

The RaspMedia Player allows remote control using simple UDP Commands. This allows to include the player in your automated environment. More details below in the section *Remote Control*.

The RaspMedia Control Desktop Application needs no further configuration, it automatically detects all players in the local network within seconds.
The RaspMedia Player can be configured over Ethernet or WiFi using a suitable WiFi USB Dongle (e.g. Asus N10). To setup WiFi the player has to be connected over Ethernet first to send suitable WiFi configurations using the desktop applications.

###Compatibility###
####Player devices####
RaspMedia is compatible with the Raspberry Pi (Model B) with Raspbian installed and with the Raspberry Clone *Banana Pi* with the *Raspbian for Banana Pi* image installed. The installation script differs between the two environments and takes care about a correct installation.
  * Note: Banana Pi uses a different default SSH login then the Raspberry Pi. Make yourself comfortable on how to log in to your device. The installation routine is then identical.

####Desktop applications####
The desktop applications for the RaspMedia player are compatible with Windows Vista/7/8 (32/64 bit), Mac OSX 10.6+, Ubuntu (12.04+) and Fedora 20. Available executables that I compile for different systems can be found at http://bit.do/raspmedia
Other operating systems then mentioned above may work but are not tested. Feel free to install the required dependencies and try to compile on other systems as well.

##Installation##
Setting up a RaspMedia player is easy, the complete installation on the raspberry pi is done using a installation script, the desktop software is written in python and can be simply compiled to an executable with pyinstaller using the provided build scripts.

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
The repository also holds three desktop applications to be used with RaspMedia Player:
   * RaspMedia Control
   * RaspMedia Copy Tool
   * RaspMedia Image Transfer

All three destop applications are compatible with Windows Vista/7/8 and Mac OSX 10.6+. *RaspMedia Control* and *RaspMedia Copy Tool* are also working with Ubuntu 12.04+ and Fedora 20.
*RaspMedia Image Transfer* is currently not working on Linux.

To use the desktop applications you have several ways:
  * Execute the main python script (needs all required packages to be installed locally)
  * Compile the application using pyinstaller and the provided *.spec* files (needs all required packages to be installed locally)
  * Executable versions of all applications can be compiled by navigating to the *Desktop* directory and executing *build_mac.sh* (Mac OS X), *build_win.bat* (Windows) or *build_linux.sh* (Ubuntu, Fedora) from there. This will compile the desktop applications, put the executable files (*.app* on Mac OS X, *.exe* on Windows, executable file on Ubuntu/Fedora) in a *Release* directory and clean up the *build* and *dist* directories. The *build_mac.sh* (Mac OS X), *build_linux.sh* (Ubuntu, Fedora) and *build_win.bat* (Windows) scripts need pyinstaller and all required packages to be installed locally as for building a single application directly with pyinstaller. If you have questions on the needed dependencies feel free to contact me.
  * Get a compiled version for your system (if available) at http://bit.do/raspmedia I will upload working executables there.

As the desktop applications are one-file-executables that have all necessary python sources packed they need no further installation. Simply copy/paste them on your PC/Mac and execute them.

####Security and Firewall####
Mac prevents the execution from applications that have not been signed by a registered Mac developer. To approve the app allthough it is from an unregeistered developer, CTRL+Click (Right-Click) on the app file and select open. A dialog box will appear asking if you are sure to launch the application from an unregistered developer. Approve the dialog by clicking 'Open'. From now on the app can be launched as any other app on your Mac.
Also make sure that your firewall (if you use one, e.g. Fedora blocked it by default when testing) does not block the program. Windows will automatically ask if you want to grant network access to the application. This approval also has to be done only once.

####RaspMedia Image Transfer and RaspMedia Control####
#####RaspMedia Image Transfer Main Window#####
RaspMedia Image Transfer allows you to fully configure and setup your RaspMedia Players. On startup the application searches for players in your local network and creates a tab for each player.
![RaspMedia Control Main Window](/Screenshots/rmi_main.png)

The main window provides a local view on the left side and a remote view on the right side. The local view shows previews of all images of the currently selected directory. You can change the directory by clicking on the button with the current path above the preview section.
By clicking single images in the two views you select which images you'd like to send to player and which images you'd like to delete from the player. The *Select All* and *Select None* Buttons below the previews speak for themselves.
By clicking *Apply* all selected remote images are deleted and all selected local images are sent to the player. It's also possible to only delete or only send images.

#####RaspMedia Control Main Window#####
RaspMedia Control allows you to fully configure and setup your RaspMedia Players. On startup the application searches for players in your local network and creates a tab for each player.
![RaspMedia Image Transfer Main Window](/Screenshots/rmc_main.png)

The main window offers information on the player (name, IP) and basic controls (Play, Stop, Reboot) at the top, by clicking identify the corresponding player will show a test image with the player name so you can identify each player and give it a appropriate name when setting up multiple players at one time.
Right underneath you can find a simple file explorer to search for images on your hard drive which you'd like to send to the player. You can send a single image by double clicking it and approving the dialog or by selecting multiple images, right click and select "Send to player".
The bottom list is the list of files you currently have on your RaspMedia Player. You can delete single files by double clicking them or again select multiple files, right click them and select "Delete from player".
If at any time you think the remote list is not up to date (which can occur due to network performance etc.) you can click "Refresh remote filelist" to update the list of files from your player.

Compared to *RaspMedia Image Transfer* this applications is a bit more generic by working with file lists and less previews. This can be very helpful when dealing with more files at once. Additionally *RaspMedia Control* allows sending and deleting video files.

#####All players tab#####
In addition to the tabs for each player, RaspMedia Image Transfer and RaspMedia Control provide the *All players* tab. This page allows you to easily get an overview on the players in your network, their IP addresses and their names. You can easily configure the names of your players or identify them as well as opening the settings window for each single player to define e.g. Image Interval etc.
![RaspMedia All Players Tab](/Screenshots/rmi_allplayers.png)

The *Master Control* section allows you to trigger certain actions for all players, including *Play*, *Stop*, *Start synced*, etc.
Below the *Master Control* section you will find the *Group* configuration. You can bind multiple players together to a group and define certain actions to be done in that group. Actions are always sent from the *Master* of the group.
To define a new action click on *Actions* in a group, select the command for the action (e.g. *Restart* wich will call a *Stop + Play*), the trigger event, the delay/periodic interval and click the *Plus* button to save the action.
![RaspMedia Control Main Window](/Screenshots/rmc_actions.png)

Trigger events can be onetime (Master has completely booted, member player comes online) with an additional delay in seconds or periodic (interval in seconds, minutes or hours) with the selected interval.
To delete an Action simply click the *X* button right to it.

A player can only belong to one single group and each group needs a master. It is also possible to create a group with only one player to be able to automate certain behaviour for this player.

#####Player Settings#####
From the *File* menu you can access the *Player Settings* to configure some playback options. On Mac OS X the player settings can be opened with the standard Keyboard Shortcut *CMD + ,*
![RaspMedia Player Settings](/Screenshots/rmc_player_settings.png)

The popping up settings window belongs to the player whose tab is currently active. The settings are self explanatory, you can enable image and video playback, select if the player should automatically start playback after booting, set the interval for image slideshows and give the player a name.
The settings also enable you to update the player to the newest version (needs internet connection).
####RaspMedia Copy Tool####
The RaspMedia Copy Tool is currently compatible with Microsoft Windows and Mac OS X. The main purpose of this application is to provide an easy way to bring media files on a RaspMedia Player for *technophobic* users.
When starting the application it searches all players in the local network. When done so it prompts to connect a USB Stick with the media files to copy to the PC.
![RaspMedia Copy Tool USB Prompt](/Screenshots/rmcopy_usb.png)

All media files (currently only images) on the root directory of the USB Stick will be copied, the order of the images used on the player depends on their filenames. When the USB stick is found the main window appears, listing the number of players found on the network, the drive letter of the USB stick (to be compared in Explorer if you like) and a scrollable preview of all images found on the USB drive that will be copied to the player(s). A checkbox allows to decide whether the images that are currently on the player should be deleted or not. Images with identical names will be overwritten.
![RaspMedia Copy Tool Main Window](/Screenshots/rmcopy_main.png)

The application allows you to send the images to all players or to a specific player. Additionally you have the possibility to start the players synchronously.

In addition to the copy feature the RaspMedia Copy Tool provides the same *Player Settings* functionality as RaspMedia Control does via the *File* menu.

##Remote Control##
The RaspMedia Player can be easyle remoted from any device (Smartphone, Desktop, etc.) using simple string commands sent over UDP. To successfully remote your player over UDP you will need to use the following setup:
  * The IP Address of your player, e.g. 192.168.0.15 (you can find out the IP using RaspMedia Control or any network tool that lists connected devices)
  * UDP Port 60001

That's all, sending the specific commands as simple strings to the IP of your player on UDP Port 60001 is all you need to do to remote control the RaspMedia Player.

###Remote Control - UDP Commands###
The following commands can be used to control playback on your RaspMedia Player:
  * *rm:state:0* --> STOP Playback (Screen blacks out)
  * *rm:state:1* --> START Playback
  * *rm:state:2* --> BLACKOUT Screen - this command has no effect by now!
  * *rm:state:3* --> PAUSE Playback
  * *rm:number:X* --> Only process file X in the list of media files (alphabetically sorted), will switch to file number X if player is already running, if player is currently stopped the command sets the filenumber and will only process that file as soon as you send a PLAY command
  * *rm:next* --> Switch to next file (only working if processing single media file set with the rm:number command)
  * *rm:prev* --> Swtich to previous file (only working if processing single media file set with the rm:number command)
  * *rm:number:-1* --> Clear a previously set media file number and process all media files.
  * *rm:hdmi:on* --> Turn on HDMI Port of RaspMedia Player
  * *rm:hdmi:off* --> Turn off HDMI Port of RaspMedia Player

In addition to the playback commands explained above, you can set some configuration values of the RaspMedia Player using the *rm:config* command with available configuration fields:
  * *rm:config:image_enabled:X* --> X=0: Disable processing of images. X=1: Enable image processing.
  * *rm:config:video_enabled:X* --> X=0: Disable processing of videos. X=1: Enable video processing.
  * *rm:config:image_interval:X* --> X = the interval in which images are changing in seconds.
  * *rm:config:player_name:name* --> name = new name for your player, avoid special characters.
  * *rm:config:autoplay:X* --> X=0/1 disable/enable autoplay, with autoplay the RaspMedia Player will start playback automatically after boot.
  * *rm:config:repeat:X* --> X=0/1 disable/enable repeating media file processing in endless loop.

###Language support###
The desktop applications *RaspMedia Control* and *RaspMedia Copy Tool* are currently available in english and german using the string files in the *lang* package (strings_de.py, strings_en.py). The language is selected according to the default locale of the system the application is started. If the language code of the default locale is unknown, english is selected as the default language.
The reading of the default locale is currently not working properly in the compiled desktop versions for Mac OS X and prevents the app from starting except when starting from the terminal. Therefor the desktop applications for Mac OS X are not compiled automatically in the correct language. Have a look in the *Localizer.py* in the *lang* package, the language code to be used (currently *DE* or *EN*) is hardcoded for Mac OS X in there.
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
