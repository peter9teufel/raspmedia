import wx, win32gui
import SettingsFrame as prefs
import packages.rmnetwork as network
import packages.rmutil as util
from packages.rmnetwork.constants import *
import sys, os, platform, time, shutil, ast
from wx.lib.pubsub import pub as Publisher
from wx.lib.wordwrap import wordwrap

playerCount = 0

HOST_WIN = 1
HOST_MAC = 2
HOST_LINUX = 3
HOST_SYS = None

BASE_PATH = None

################################################################################
# MAIN FRAME OF APPLICATION ####################################################
################################################################################
class SimpleUIAppFrame(wx.Frame):
    def __init__(self,parent,id,title,base_path):
        wx.Frame.__init__(self,parent,id,title,size=(200,300))
        self.parent = parent
        self.base_path = base_path
        self.Bind(wx.EVT_CLOSE, self.Close)
        self.SetupMenuBar()

        self.hostSearch = False
        self.udpListening = False
        self.deleteFiles = True
        self.hosts = []
        self.filesToCopy = []
        self.activePageNr = 0
        global HOST_SYS, BASE_PATH
        BASE_PATH = base_path
        # check platform
        if platform.system() == 'Windows':
            HOST_SYS = HOST_WIN
        elif platform.system() == 'Darwin':
            HOST_SYS = HOST_MAC
        elif platform.system() == 'Linux':
            HOST_SYS = HOST_LINUX

        self.Center()
        self.Show()
        print "Starting host search..."
        self.SearchHosts()


    def HostFound(self, host, playerName):
        global playerCount
        print "Adding host to list..."
        if not self.HostInList(host[0], playerName):
            self.hosts.append({"addr": host[0], "name": playerName})
            playerCount += 1

    def HostInList(self, addr, playerName):
        for h in self.hosts:
            if h['addr'] == addr and h['name'] == playerName:
                return True
        return False

    def SearchHosts(self):
        self.hostSearch = True
        self.udpListening = True
        Publisher.subscribe(self.HostFound, 'host_found')
        Publisher.subscribe(self.UdpListenerStopped, 'listener_stop')
        msgData = network.messages.getMessage(SERVER_REQUEST)
        self.prgDialog = wx.ProgressDialog("Searching...", "Searching available RaspMedia Players...", parent = self, style = wx.PD_AUTO_HIDE)
        self.prgDialog.Pulse()
        network.udpconnector.sendMessage(msgData)

    def UdpListenerStopped(self):
        global playerCount
        self.udpListening = False
        Publisher.unsubscribe(self.UdpListenerStopped, 'listener_stop')
        Publisher.unsubscribe(self.HostFound, 'host_found')
        print "Number of players found: ", playerCount
        if self.hostSearch:
            self.hostSearch = False
            if playerCount == 0:
                self.prgDialog.Update(100)
                if HOST_SYS == HOST_WIN:
                    self.prgDialog.Destroy()
                dlg = wx.SingleChoiceDialog(self,wordwrap("No RaspMedia Players found, check if your players are running and connected to the local network.", 300, wx.ClientDC(self)), "No Player found", ['Rescan', 'Exit'])
                result = dlg.ShowModal()
                selection = dlg.GetSelection()
                print "RESULT: ", result
                if result == wx.ID_OK:
                    print "OK clicked, checking selected index... ", selection
                    if selection == 0: # RESCAN
                        self.SearchHosts()
                    #elif selection == 1:
                    #   pass
                    elif selection == 1: # EXIT
                        self.Close()
                elif result == wx.ID_CANCEL:
                    print "Cancel clicked, terminating program, bye bye..."
                    self.Close()
            else:
                self.WaitForUSB()

    def Close(self, event=None):
        Publisher.unsubAll()
        if self.udpListening:
            print "Destroying UDP Response Listener..."
            network.udpresponselistener.destroy()
        self.Destroy()

    def WaitForUSB(self):
        self.prgDialog.UpdatePulse("Please plug in your USB drive now...")
        print "Waiting for USB Drive..."
        Publisher.subscribe(self.USBConnected, 'usb_connected')
        util.Win32DeviceDetector.waitForUSBDrive()


    def USBConnected(self, path):
        # Publisher.unsubscribe(self.USBConnected, 'usb_connected')
        print "USB Drive connected and mounted in %s:" % path
        print "Scanning files in root directory of %s:" % path
        self.prgDialog.UpdatePulse("USB drive found, scanning for images...")
        time.sleep(2)
        # add colon as path is only the drive letter of the connected USB drive
        self.usbPath = path + ':'
        self.ScanFolder(path + ':')
        
    def ScanFolder(self, path):
        for file in os.listdir(path):
            if not file.startswith(".") and file.endswith((SUPPORTED_IMAGE_EXTENSIONS)):
                # image file found --> add to list of files to copy
                self.filesToCopy.append(file)
        
        self.prgDialog.Update(100)
        if HOST_SYS == HOST_WIN:
            self.prgDialog.Destroy()
        if len(self.filesToCopy) == 0:
            # no images found on USB drive root
            msg = "No images found on USB drive. Make sure the images are in the root path. Try again?"
            dlg = wx.MessageDialog(self, msg, "No files found", wx.YES_NO | wx.ICON_QUESTION)
            if dlg.ShowModal() == wx.ID_YES:
                self.prgDialog = wx.ProgressDialog("Waiting for USB...", "Please plug in your USB drive now...", parent = self, style = wx.PD_AUTO_HIDE)
                self.prgDialog.Pulse()
                if HOST_SYS == HOST_WIN:
                    dlg.Destroy()
            else:
                if HOST_SYS == HOST_WIN:
                    dlg.Destroy()
                self.Close()
        else:
            # image files found --> proceed
            print "Image files found in %s" % path
            print self.filesToCopy
            self.Raise()
            self.InitUI()
            


    def SetupMenuBar(self):
        # menus
        fileMenu = wx.Menu()
        helpMenu = wx.Menu()

        # File Menu
        menuSettings = fileMenu.Append(wx.ID_ANY, "&Player Settings", "Player Settings")
        menuExit = fileMenu.Append(wx.ID_EXIT, "&Exit"," Terminate the program")
        self.Bind(wx.EVT_MENU, self.Close, menuExit)
        self.Bind(wx.EVT_MENU, self.ShowPlayerSettings, menuSettings)

        # Help Menu
        about = helpMenu.Append(wx.ID_ANY, "&About")
        self.Bind(wx.EVT_MENU, self.ShowAbout, about)

        # Menubar
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File") # Adding the "filemenu" to the MenuBar

        menuBar.Append(helpMenu, "&About")
        self.SetMenuBar(menuBar)

    def InitUI(self):
        self.mainSizer = wx.GridBagSizer()
        self.InitStatusUI()

        # add chkbox for file deletion
        delFiles = wx.CheckBox(self, -1, "Delete current files from player")
        delFiles.SetValue(True)

        self.Bind(wx.EVT_CHECKBOX, self.DeleteFilesToggled, delFiles)

        self.mainSizer.Add(delFiles, (4,0), flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, border = 10)

        # add buttons
        send2All = wx.Button(self, -1, "Send to all players")
        send2One = wx.Button(self, -1, "Send to specific player")
        exitBtn = wx.Button(self, -1, "Exit")

        self.Bind(wx.EVT_BUTTON, self.SendToAllPlayers, send2All)
        self.Bind(wx.EVT_BUTTON, self.SendToSpecificPlayer, send2One)
        self.Bind(wx.EVT_BUTTON, self.Close, exitBtn)

        self.mainSizer.Add(send2All, (5,0), flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, border = 5)
        self.mainSizer.Add(send2One, (6,0), flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, border = 5)
        self.mainSizer.Add(exitBtn, (7,0), flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, border = 5)

        self.SetSizerAndFit(self.mainSizer)
        self.Center()

    def DeleteFilesToggled(self, event):
        checkbox = event.GetEventObject()
        self.deleteFiles = checkbox.IsChecked()
        print "Delete files: ", self.deleteFiles

    def SendToAllPlayers(self, event=None):
        for host in self.hosts:
            if self.deleteFiles:
                self.DeleteFilesFromPlayer(host)
            self.SendFilesToPlayer(host)

    def SendFilesToPlayer(self, host):
        files = self.filesToCopy
        # optimize the files before sending them
        # create temp directory
        tmpPath = BASE_PATH + '/' + 'tmp'
        if os.path.isdir(tmpPath):
            print "Removing old temp directory..."
            shutil.rmtree(tmpPath)
        try:
            os.makedirs(tmpPath)
        except OSError as exception:
            print "Exception in creating DIR: ",exception
        util.ImageUtil.OptimizeImages(files, self.usbPath, tmpPath,1920,1080,HOST_SYS == HOST_WIN)
        network.tcpfileclient.sendFiles(files, tmpPath, host['addr'], self, HOST_SYS == HOST_WIN)
        print "Deleting temporary files..."
        shutil.rmtree(tmpPath)
        dlg = wx.ProgressDialog("Saving", "Saving files on player...", style = wx.PD_AUTO_HIDE)
        dlg.Pulse()
        numFiles = len(files)
        # give the player at least 0.2s per file to save
        time.sleep(numFiles * 0.4)
        dlg.Update(100)
        if HOST_SYS == HOST_WIN:
            dlg.Destroy()

        # restart player
        print "Restarting player..."
        msgData = network.messages.getMessage(PLAYER_RESTART)
        network.udpconnector.sendMessage(msgData, host['addr'])


    def DeleteFilesFromPlayer(self, host):
        msgData = network.messages.getMessage(DELETE_ALL_IMAGES)
        network.udpconnector.sendMessage(msgData, host['addr'])

    def SendToSpecificPlayer(self, event=None):
        host = self.HostSelection()
        if not host == None:
            self.SendFilesToPlayer(host)

    def HostSelection(self):
        items = []
        resultHost = None
        for host in self.hosts:
            items.append("%s | %s" % (host['name'], host['addr']))
        dlg = wx.SingleChoiceDialog(self,wordwrap("Select a player:", 300, wx.ClientDC(self)), "RaspMedia Players", items)
        result = dlg.ShowModal()
        selection = dlg.GetSelection()
        print "RESULT: ", result
        if result == wx.ID_OK:
            resultHost = self.hosts[selection]
            print "SELECTED HOST: ", resultHost

        return resultHost

    def InitStatusUI(self):
        # init status labels
        numPlayers = len(self.hosts)
        if numPlayers == 1:
            players = "%d player found in local network." % numPlayers
        else:
            players = "%d players found in local network." % numPlayers
        playersLabel = wx.StaticText(self, -1, label=players)
        usbInfo = "Detected USB drive %s" % self.usbPath
        usbLabel = wx.StaticText(self, -1, label=usbInfo)
        imgInfo = "Images found in USB root: %d" % len(self.filesToCopy)
        imgLabel = wx.StaticText(self, -1, label=imgInfo)

        # add to main sizer
        self.mainSizer.Add(playersLabel, (0,0), flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP | wx.LEFT | wx.RIGHT, border = 10)
        self.mainSizer.Add(usbLabel, (1,0), flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP | wx.LEFT | wx.RIGHT, border = 10)
        self.mainSizer.Add(imgLabel, (2,0), flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, border = 10)

    def ShowAbout(self, event):
        # message read from defined version info file in the future
        msg = "RaspMedia Copy Tool v1.0\n(c) 2014 by www.multimedia-installationen.at\nContact: software@multimedia-installationen.at\nAll rights reserved."
        dlg = wx.MessageDialog(self, msg, "About", style=wx.OK)
        dlg.ShowModal()

    def ShowPlayerSettings(self, event):
        host = self.HostSelection()
        if not host == None:
            self.configHost = host
            self.LoadRemoteConfig(host)

    def SettingsClosedWithConfig(self, config):
        self.config = config
        for host in self.hosts:
            if host['addr'] == self.configHost['addr']:
                host['name'] = self.config['player_name']

    def LoadRemoteConfig(self, host):
        print "Entering LoadRemoteConfig routine...."
        Publisher.subscribe(self.ConfigLoaded, 'config')
        print "Observers registered..."

        msgData = network.messages.getMessage(CONFIG_REQUEST)
        network.udpconnector.sendMessage(msgData, host['addr'])

    def ConfigLoaded(self, config, isDict=False):
        Publisher.unsubscribe(self.ConfigLoaded, 'config')
        global HOST_SYS
        if isDict:
            configDict = config
        else:
            configDict = ast.literal_eval(config)
        print configDict
        self.config = configDict
        
        # config loaded --> settings can be opened now
        settings = prefs.SettingsFrame(self,-1,"Player Settings",self.configHost, self.config)
        settings.Center()
        settings.SetBackgroundColour('WHITE')
        settings.Refresh()
        settings.Show()