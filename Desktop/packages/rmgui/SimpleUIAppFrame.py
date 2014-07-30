# -*- coding: utf-8 -*-
import wx
import SettingsFrame as prefs
import ScrollableImageView as scrollable
import packages.rmnetwork as network
import packages.rmutil as util
from packages.rmnetwork.constants import *
import sys, os, platform, time, shutil, ast
from wx.lib.pubsub import pub as Publisher
from wx.lib.wordwrap import wordwrap
from packages.lang.Localizer import *

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
        wx.Frame.__init__(self,parent,id,title,size=(200,100))
        self.parent = parent
        self.base_path = base_path
        self.Bind(wx.EVT_CLOSE, self.Close)
        self.hostSearch = False
        self.udpListening = False
        self.deleteFiles = True
        self.hosts = []
        self.filesToCopy = []
        self.filePaths = []
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
        self.SetBackgroundColour('WHITE')
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
        self.prgDialog = wx.ProgressDialog(tr("searching"), tr("searching_players"), parent = self, style = wx.PD_AUTO_HIDE)
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
                #dlg = wx.SingleChoiceDialog(self,wordwrap(tr("no_players_found"), 300, wx.ClientDC(self)), tr("no_player"), [tr("rescan"), tr("exit")])
                dlg = wx.MessageDialog(self,wordwrap(tr("no_players_found"), 300, wx.ClientDC(self)), tr("no_player"), style=wx.YES_NO)
                result = dlg.ShowModal()
                #selection = dlg.GetSelection()
                print "RESULT: ", result
                if result == wx.ID_YES:
                    #if selection == 0: # RESCAN
                    self.SearchHosts()
                    #elif selection == 1:
                    #   pass
                    #elif selection == 1: # EXIT
                    #    self.Close()
                elif result == wx.ID_NO:
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
        os._exit(0)

    def WaitForUSB(self):
        if HOST_SYS == HOST_WIN:
            util.Win32DeviceDetector.waitForUSBDrive()
        elif HOST_SYS == HOST_MAC:
            util.MacDriveDetector.waitForUSBDrive()
        self.prgDialog.UpdatePulse(tr("plug_usb"))
        print "Waiting for USB Drive..."
        Publisher.subscribe(self.USBConnected, 'usb_connected')


    def USBConnected(self, path):
        # Publisher.unsubscribe(self.USBConnected, 'usb_connected')
        print "USB Drive connected and mounted in path %s" % path
        print "Scanning files in root directory of path %s" % path
        self.prgDialog.UpdatePulse(tr("usb_found_scan"))
        time.sleep(2)
        if HOST_SYS == HOST_WIN:
            # add colon as path is only the drive letter of the connected USB drive
            path += ":"

        self.usbPath = path
        self.ScanFolder(path)

    def ScanFolder(self, path):
        for file in os.listdir(path):
            if not file.startswith(".") and file.endswith((SUPPORTED_IMAGE_EXTENSIONS)):
                # image file found --> add to list of files to copy
                self.filesToCopy.append(file)
                self.filePaths.append(path + '/' + file)

        self.prgDialog.Update(100)
        if HOST_SYS == HOST_WIN:
            self.prgDialog.Destroy()
        if len(self.filesToCopy) == 0:
            # no images found on USB drive root
            msg = tr("usb_no_images_found")
            dlg = wx.MessageDialog(self, msg, tr("no_files_found"), wx.YES_NO | wx.ICON_QUESTION)
            if dlg.ShowModal() == wx.ID_YES:
                self.prgDialog = wx.ProgressDialog(tr("waiting_for_usb"), tr("plug_usb"), parent = self, style = wx.PD_AUTO_HIDE)
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

    def InitUI(self):
        self.mainSizer = wx.GridBagSizer()
        self.InitStatusUI()

        # add chkbox for file deletion
        delFiles = wx.CheckBox(self, -1, tr("delete_current_files"))
        delFiles.SetValue(True)

        self.Bind(wx.EVT_CHECKBOX, self.DeleteFilesToggled, delFiles)

        self.mainSizer.Add(delFiles, (2,1), span=(1,2), flag=wx.LEFT | wx.TOP, border = 5)
        info = wx.StaticText(self, -1, label=wordwrap(tr("copy_deletion_info"), 400, wx.ClientDC(self)))
        self.mainSizer.Add(info, (3,1), span=(1,2), flag=wx.LEFT, border=5)

        #load bitmaps for buttons
        path = resource_path("img/ic_sendtoall.png")
        ic_send2all = util.ImageUtil.DrawCaption(path, tr("send_to_all"))
        path = resource_path("img/ic_sendtoone.png")
        ic_send2one = util.ImageUtil.DrawCaption(path, tr("send_to_one"))
        path = resource_path("img/ic_startsynced.png")
        ic_startSynced = util.ImageUtil.DrawCaption(path, tr("restart_all"))
        path = resource_path("img/ic_exit.png")
        ic_exit = util.ImageUtil.DrawCaption(path, tr("exit"))

        # add bitmap buttons
        send2All = wx.BitmapButton(self, -1, ic_send2all, size=(200,200))
        send2One = wx.BitmapButton(self, -1, ic_send2one, size = (200,200))
        restartAll = wx.BitmapButton(self, -1, ic_startSynced, size=(200,200))
        exitBtn = wx.BitmapButton(self, -1, ic_exit, size=(200,200))

        self.Bind(wx.EVT_BUTTON, self.SendToAllPlayers, send2All)
        self.Bind(wx.EVT_BUTTON, self.SendToSpecificPlayer, send2One)
        self.Bind(wx.EVT_BUTTON, self.RestartAllPlayers, restartAll)
        self.Bind(wx.EVT_BUTTON, self.Close, exitBtn)

        self.mainSizer.Add(send2All, (0,1), flag=wx.ALL | wx.ALIGN_RIGHT, border = 2)
        self.mainSizer.Add(send2One, (0,2), flag=wx.ALL | wx.ALIGN_RIGHT, border = 2)
        self.mainSizer.Add(restartAll, (1,1), flag=wx.ALL | wx.ALIGN_LEFT, border = 2)
        self.mainSizer.Add(exitBtn, (1,2), flag=wx.ALL | wx.ALIGN_LEFT, border = 2)

        self.SetupMenuBar()

        self.SetSizerAndFit(self.mainSizer)
        self.Center()

    def InitStatusUI(self):
        statusBox = wx.BoxSizer(orient=wx.VERTICAL)

        # init status labels
        numPlayers = len(self.hosts)
        if numPlayers == 1:
            players = tr("one_player_found")
        else:
            players = "%s %d %s" % (tr("multiple_players_one"),numPlayers,tr("multiple_players_two"))

        #for host in self.hosts:
        #    players += host['name'] + "\n"

        status =  wordwrap("%s\n\n%s %s\n%d %s\n" % (players,tr("usb_at_drive"),self.usbPath,len(self.filesToCopy),tr("images_available")), 300, wx.ClientDC(self))

        statusLabel = wx.StaticText(self, -1, label=status)

        #usbTxt = wx.TextCtrl(self, -1, size=(300,280), style = wx.TE_READONLY | wx.TE_MULTILINE)

        #for file in self.filesToCopy:
        #    usbTxt.AppendText(file + "\n")

        imgPrevH = 480 - statusLabel.GetSize()[1]

        imageView = scrollable.ScrollableImageView(self, -1, (300,imgPrevH), self.filePaths)

        # add to status view sizer
        statusBox.Add(statusLabel, flag = wx.LEFT | wx.TOP | wx.RIGHT, border=5)
        statusBox.Add(imageView, flag = wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5)

        # add to main sizer
        self.mainSizer.Add(statusBox, (0,0), span=(4,1))
        #self.mainSizer.Add(statusLabel, (0,0), span=(1,1), flag = wx.ALL, border = 5)
        #self.mainSizer.Add(imageView, (1,0), span=(3,1), flag = wx.LEFT | wx.BOTTOM | wx.RIGHT, border = 5)

    def SetupMenuBar(self):
        strAbout = tr("about")
        strFile = tr("file")

        # menus
        fileMenu = wx.Menu()
        helpMenu = wx.Menu()

        # File Menu
        strSettings = tr("player_settings")
        strExit = tr("exit")

        # create submenu to launch settings for specific player
        settingsMenu = wx.Menu()

        # append entry for each found player
        for host in self.hosts:
            menuHost = settingsMenu.Append(wx.ID_ANY, host['name'])
            self.Bind(wx.EVT_MENU, lambda event, host=host: self.ShowPlayerSettings(event,host), menuHost)

        # append items to file menu
        fileMenu.AppendMenu(wx.ID_ANY, strSettings, settingsMenu)
        menuExit = fileMenu.Append(wx.ID_EXIT, "&"+strExit, strExit)

        self.Bind(wx.EVT_MENU, self.Close, menuExit)

        # Help Menu
        about = helpMenu.Append(wx.ID_ANY, "&"+strAbout)
        self.Bind(wx.EVT_MENU, self.ShowAbout, about)

        # Menubar
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&"+strFile) # Adding the "filemenu" to the MenuBar

        menuBar.Append(helpMenu, "&"+strAbout)
        self.SetMenuBar(menuBar)

    def DeleteFilesToggled(self, event):
        checkbox = event.GetEventObject()
        self.deleteFiles = checkbox.IsChecked()
        print "Delete files: ", self.deleteFiles

    def RestartAllPlayers(self, event=None):
        msgData = network.messages.getMessage(PLAYER_RESTART)
        network.udpconnector.sendMessage(msgData)
        dlg = wx.MessageDialog(self, tr("done"), tr("done"), style = wx.OK)
        dlg.ShowModal()

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
        dlg = wx.ProgressDialog(tr("saving"), tr("saving_files_player"), style = wx.PD_AUTO_HIDE)
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
        dlg = wx.SingleChoiceDialog(self,wordwrap(tr("select_player"), 300, wx.ClientDC(self)), tr("rasp_players"), items)
        result = dlg.ShowModal()
        selection = dlg.GetSelection()
        print "RESULT: ", result
        if result == wx.ID_OK:
            resultHost = self.hosts[selection]
            print "SELECTED HOST: ", resultHost

        return resultHost

    def ShowAbout(self, event):
        # message read from defined version info file in the future
        msg = "RaspMedia Copy Tool v1.0\n(c) 2014 by www.multimedia-installationen.at\nContact: software@multimedia-installationen.at\nAll rights reserved."
        dlg = wx.MessageDialog(self, msg, "About", style=wx.OK)
        dlg.ShowModal()

    def ShowPlayerSettings(self, event, host):
        #host = self.HostSelection()
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
        settings = prefs.SettingsFrame(self,-1,tr("player_settings"),self.configHost, self.config)
        settings.Center()
        settings.SetBackgroundColour('WHITE')
        settings.Refresh()
        settings.Show()


# HELPER METHOD to get correct resource path for image file
def resource_path(relative_path):
    global BASE_PATH
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
        #print "BASE PATH FOUND: "+ base_path
    except Exception:
        #print "BASE PATH NOT FOUND!"
        base_path = BASE_PATH
    #print "JOINING " + base_path + " WITH " + relative_path
    resPath = os.path.normcase(os.path.join(base_path, relative_path))
    #resPath = base_path + relative_path
    #print resPath
    return resPath
