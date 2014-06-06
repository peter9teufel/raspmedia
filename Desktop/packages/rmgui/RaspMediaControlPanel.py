import packages.rmnetwork as network
import packages.rmutil as rmutil
from packages.rmgui import *
from packages.rmnetwork.constants import *
import os, sys, platform, ast, time, threading, shutil

import wx
from wx.lib.pubsub import pub as Publisher
from wx.lib.wordwrap import wordwrap

HOST_WIN = 1
HOST_MAC = 2
HOST_LINUX = 3
HOST_SYS = None
BASE_PATH = None

################################################################################
# RASP MEDIA CONTROL PANEL #####################################################
################################################################################
class RaspMediaCtrlPanel(wx.Panel):
    def __init__(self,parent,id,title,index,host,host_sys):
        #wx.Panel.__init__(self,parent,id,title)
        wx.Panel.__init__(self,parent,-1)
        global HOST_SYS, BASE_PATH
        HOST_SYS = host_sys
        BASE_PATH = parent.parent.base_path
        self.parent = parent
        self.index = index
        self.host = host
        self.path = self.DefaultPath()
        self.mainSizer = wx.GridBagSizer()
        self.configSizer = wx.GridBagSizer()
        self.playerSizer = wx.GridBagSizer()
        self.filesSizer = wx.GridBagSizer()
        self.notebook_event = None
        self.prgDialog = None
        self.pageDataLoading = False
        self.remoteListLoading = False
        self.shiftDown = False
        self.Initialize()

    def OnKeyDown(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_SHIFT:
            self.shiftDown = True
        event.Skip()

    def OnKeyUp(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_SHIFT:
            self.shiftDown = False

    def DefaultPath(self):
        path = os.path.expanduser("~")
        result = path
        # try common image directory paths
        if os.path.isdir(path + '/Bilder'):
            result = path + '/Bilder'
        elif os.path.isdir(path + '/Eigene Bilder'):
            result = path + '/Eigene Bilder'
        elif os.path.isdir(path + '/Pictures'):
            result = path + '/Pictures'
        elif os.path.isdir(path + '/Images'):
            result = path + '/Images'
        return result

    def SetHost(self, hostAddress):
        self.host = hostAddress

    def LoadData(self):
        self.pageDataLoading = True
        self.remoteListLoading = False
        # subscribe for async callbacks
        Publisher.subscribe(self.UpdateConfigUI, 'config')
        Publisher.subscribe(self.InsertReceivedFileList, 'remote_files')
        Publisher.subscribe(self.UdpListenerStopped, 'listener_stop')
        # start loading data
        self.prgDialog = wx.ProgressDialog("Loading...", "Loading configuration and filelist from player...")
        self.prgDialog.Pulse()
        self.LoadRemoteConfig()

    def PageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.parent.GetSelection()
        self.notebook_event = event
        print "OnPageChanged, old:%d, new:%d, sel:%d" % (old, new, sel)
        newPage = self.parent.GetPage(new)
        if self.index == newPage.index:
            print "PAGE CHANGED TO INDEX %d - PROCESSING AND LOADING DATA..." % (self.index)
            self.pageDataLoading = True
            self.LoadData()

    def Initialize(self):
        print "Setting up player section..."
        self.SetupPlayerSection()
        print "Setting up file lists..."
        self.SetupFileLists()

        self.mainSizer.Add(self.playerSizer,(0,0), flag=wx.ALIGN_CENTER_HORIZONTAL | wx.LEFT | wx.RIGHT, border=10)
        self.mainSizer.Add(self.configSizer, (0,2), flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, border=10)

        self.mainSizer.Add(self.filesSizer, (2,0), span=(1,4), flag=wx.BOTTOM | wx.LEFT | wx.RIGHT, border=10)

        self.SetSizerAndFit(self.mainSizer)

        line = wx.StaticLine(self,-1,size=(self.mainSizer.GetSize()[0],2))
        self.mainSizer.Add(line, (1,0), span=(1,4))

        line = wx.StaticLine(self,-1,size=(2,self.mainSizer.GetCellSize(0,0)[1]),style=wx.LI_VERTICAL)
        self.mainSizer.Add(line,(0,1), flag = wx.LEFT, border = 10)

        self.Fit()
        psHeight = self.playerSizer.GetSize()[1]
        print "PlayerSizer height: ",psHeight
        line = wx.StaticLine(self,-1,size=(2,psHeight),style=wx.LI_VERTICAL)
        self.playerSizer.Add(line,(0,2), span=(3,1), flag=wx.LEFT | wx.RIGHT, border=5)

        # self.SetSizeHints(self.GetSize().x,self.GetSize().y,-1,self.GetSize().y)
        #self.SetSizerAndFit(self.mainSizer)
        self.Show(True)

    def SetupPlayerSection(self):
        # Text label
        label = wx.StaticText(self,-1,label="Remote Control:")
        self.playerSizer.Add(label,(0,0),(1,2), flag = wx.TOP | wx.BOTTOM, border=5)

        # player name and address
        nameLabel = wx.StaticText(self,-1,label="Player name: ")
        self.playerNameLabel = wx.StaticText(self,-1,label="", size = (130,nameLabel.GetSize()[1]))
        addrLabel = wx.StaticText(self,-1,label="IP-Address: ")
        playerAddr = wx.StaticText(self,-1,label=self.host)
        self.playerSizer.Add(nameLabel, (1,0), flag=wx.ALIGN_CENTER_VERTICAL)
        self.playerSizer.Add(self.playerNameLabel, (1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        self.playerSizer.Add(addrLabel, (2,0), flag = wx.ALIGN_CENTER_VERTICAL)
        self.playerSizer.Add(playerAddr, (2,1), flag = wx.ALIGN_CENTER_VERTICAL)

        # Play and Stop Button
        button = wx.Button(self,-1,label="Play")
        self.playerSizer.Add(button,(1,3))
        self.Bind(wx.EVT_BUTTON, self.PlayClicked, button)

        button = wx.Button(self,-1,label="Stop")
        self.playerSizer.Add(button,(2,3), flag=wx.TOP, border=5)
        self.Bind(wx.EVT_BUTTON, self.StopClicked, button)

        button = wx.Button(self,-1,label="Identify")
        button.SetName("btn_identify")
        self.playerSizer.Add(button,(1,5), flag = wx.BOTTOM, border = 5)
        self.Bind(wx.EVT_BUTTON, self.ButtonClicked, button)

        button = wx.Button(self,-1,label="Reboot")
        button.SetName("btn_reboot")
        self.playerSizer.Add(button,(2,5), flag=wx.TOP | wx.BOTTOM, border=5)
        self.Bind(wx.EVT_BUTTON, self.ButtonClicked, button)

    def SetupFileLists(self):
        self.filesSizer.SetEmptyCellSize((0,0))
        # setup file lists and image preview
        self.AddLocalList()
        self.AddImagePreview()
        self.AddRemoteList()

        selectFolder = wx.Button(self,-1,label="Select directory...")
        self.filesSizer.Add(selectFolder, (0,0), flag = wx.TOP | wx.BOTTOM, border = 5)
        self.Bind(wx.EVT_BUTTON, self.ChangeDir, selectFolder)

        button = wx.Button(self,-1,label="Refresh remote filelist")
        self.filesSizer.Add(button,(4,0))
        self.Bind(wx.EVT_BUTTON, self.LoadRemoteFileList, button)
        self.filesSizer.Fit(self)

    def AddLocalList(self):
        print "Initializing empty local lists..."
        self.localList = wx.ListCtrl(self,-1,size=(400,220),style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        print "Showing list..."
        self.localList.Show(True)
        self.localList.InsertColumn(0,"Filename", width = 300)
        self.localList.InsertColumn(1,"Filesize", width = 80, format = wx.LIST_FORMAT_RIGHT)
        self.filesSizer.Add(self.localList, (1,0), span=(2,1))
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.LocalFileDoubleClicked, self.localList)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.LocalFileSelected, self.localList)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.LocalFileRightClicked, self.localList)

        self.localList.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.localList.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.UpdateLocalFiles()

    def AddImagePreview(self):
        img = wx.EmptyImage(200,200)
        # create bitmap with preview png
        self.imageCtrl = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(img))
        self.SetPreviewImage('img/preview.png')
        self.filesSizer.Add(self.imageCtrl, (1,1), flag = wx.LEFT, border=5)

        # add static label to show selected filename or number of selected files
        self.selectionLabel = wx.StaticText(self,-1,label="")
        self.filesSizer.Add(self.selectionLabel, (2,1), flag = wx.LEFT, border = 15)

    def AddRemoteList(self):
        print "Initializing empty remote lists..."
        self.remoteList=wx.ListCtrl(self,-1,size=(600,200),style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.remoteList.Show(True)
        self.remoteList.InsertColumn(0,"Remote Files: ", width = 598)
        self.filesSizer.Add(self.remoteList, (3,0), span=(1,2), flag = wx.EXPAND | wx.TOP, border = 10)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.RemoteFileDoubleClicked, self.remoteList)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.RemoteFileRightClicked, self.remoteList)

    def UpdateLocalFiles(self):
        self.localList.DeleteAllItems()

        if not self.path.endswith(':') or not len(self.path <= 1):
            self.localList.InsertStringItem(0, '..')

        folders = []
        files = []
        for file in os.listdir(self.path):
            if not file.startswith(('$','.')):
                imgOrVideo = file.endswith((SUPPORTED_IMAGE_EXTENSIONS)) or file.endswith((SUPPORTED_VIDEO_EXTENSIONS))
                if imgOrVideo:
                    files.append({"filename": file, "size": os.stat(self.path + '/' + file).st_size})
                elif os.path.isdir(self.path + '/' + file):
                    folders.append(file)

        for folderName in folders:
            self.localList.InsertStringItem(self.localList.GetItemCount(), folderName)

        for curFile in files:
            idx = self.localList.InsertStringItem(self.localList.GetItemCount(), curFile['filename'])
            size = curFile['size']
            size = round(size / 1024 / 1024.0, 1)
            sizeStr = str(size) + "MB"
            self.localList.SetStringItem(idx, 1, sizeStr)

        #col = self.localList.GetColumn(0)
        #col.SetText(self.path)
        #self.localList.SetColumn(0, col)

    def InsertReceivedFileList(self, serverAddr, files):
        print "UPDATING REMOTE FILELIST UI..."
        self.remoteList.DeleteAllItems()
        files.sort()
        for file in reversed(files):
            if not file.startswith('.') and '.' in file:
                self.remoteList.InsertStringItem(0, file)

    def UpdateConfigUI(self, config, isDict=False):
        global HOST_SYS
        if isDict:
            configDict = config
        else:
            configDict = ast.literal_eval(config)
        print configDict
        self.config = configDict
        self.playerNameLabel.SetLabel(configDict['player_name'])
        #if self.notebook_event:
        #	self.parent.SetPageText(self.notebook_event.GetSelection(), str(configDict['player_name']))
        #else:
        self.parent.SetPageText(self.parent.GetSelection(), str(configDict['player_name']))
        self.parent.parent.Refresh()

    def GetLocalSelectionInfo(self):
        mixed = False
        prevType = None
        index = self.localList.GetFirstSelected()
        cnt = 0
        files = []
        while not index == -1:
            item = self.localList.GetItem(index,0)
            files.append(item.GetText())
            filePath = self.path + '/' + item.GetText()
            curType = None
            if filePath.endswith((SUPPORTED_VIDEO_EXTENSIONS)) or filePath.endswith((SUPPORTED_IMAGE_EXTENSIONS)):
                curType = 'media'
            elif os.path.isdir(filePath):
                curType = 'dir'
            if prevType and curType and not curType == prevType:
                mixed = True
            cnt += 1
            index = self.localList.GetNextSelected(index)
        if mixed:
            resType = "mixed"
        else:
            resType = curType
        return {"count": cnt, "type": resType, "files": files}

    def MutlipleLocalFilesSelected(self):
        index = self.localList.GetFirstSelected()
        if index == -1:
            return False
        else:
            if self.localList.GetNextSelected(index) == -1:
                return False
            else:
                return True
        return False

    def LocalFileSelected(self, event):
        filePath = None
        sel = self.GetLocalSelectionInfo()
        # preview if only one file selected or multiple without shift key for quick selection
        if sel['count'] == 1 or (sel['count'] > 1 and not self.shiftDown):
            filePath = self.path + '/' +  event.GetText()
            if sel['count'] == 1:
                if sel['type'] == 'media':
                    self.selectionLabel.SetLabel(event.GetText())
                else:
                    self.selectionLabel.SetLabel("")
            else:
                self.selectionLabel.SetLabel(self.GetSelectionLabelText(sel))
        else:
            self.selectionLabel.SetLabel(self.GetSelectionLabelText(sel))

        if filePath:
            imagePath = filePath

            if filePath.endswith((SUPPORTED_VIDEO_EXTENSIONS)):
                imagePath = 'img/video.png'
            elif os.path.isdir(filePath):
                imagePath = 'img/preview.png'

            self.SetPreviewImage(imagePath)

    def GetSelectionLabelText(self, sel):
        files = sel['files']
        selLabel = ""
        if sel['count'] > 1:
            if sel['type'] == 'media':
                selLabel = "%d Mediafiles selected" % (len(files))
            elif sel['type'] == 'dir':
                selLabel = "Multiple directories selected"
            else:
                selLabel = "%d selected (Mediafiles and directories)" % (len(files))
        return selLabel

    def LocalFileRightClicked(self, event):
        global HOST_SYS
        file = event.GetText()
        menu = wx.Menu()
        if file == '..' or os.path.isdir(self.path + '/' + file):
            item = menu.Append(wx.NewId(), "Open")
            self.Bind(wx.EVT_MENU, self.ShowSelectedDirectory, item)
        else:
            item = menu.Append(wx.NewId(), "Send to Player")
            self.Bind(wx.EVT_MENU, self.SendSelectedFilesToPlayer, item)
        rect = self.localList.GetRect()
        point = event.GetPoint()
        if HOST_SYS == HOST_WIN:
            self.PopupMenu(menu, (rect[0]+point[0]+10,rect[1]+point[1]+10))
        else:
            self.PopupMenu(menu, (rect[0]+point[0]+10,rect[1]+point[1]+30))
        menu.Destroy()

    def ShowSelectedDirectory(self, event):
        folder = self.localList.GetItemText(self.localList.GetFocusedItem())
        if folder == '..':
            self.ShowParentDirectory()
        else:
            newPath = self.path + '/' + folder
            self.ShowDirectory(newPath)

    def RemoteFileRightClicked(self, event):
        file = event.GetText()
        menu = wx.Menu()
        item = menu.Append(wx.NewId(), "Delete")
        self.Bind(wx.EVT_MENU, self.DeleteSelectedRemoteFile, item)
        rect = self.remoteList.GetRect()
        point = event.GetPoint()
        if HOST_SYS == HOST_WIN:
            self.PopupMenu(menu, (rect[0]+point[0]+10,rect[1]+point[1]+10))
        else:
            self.PopupMenu(menu, (rect[0]+point[0]+10,rect[1]+point[1]+30))
        menu.Destroy()

    def DeleteSelectedRemoteFile(self, event):
        index = self.remoteList.GetFirstSelected()
        files = []
        while not index == -1:
            item = self.remoteList.GetItem(index,0)
            fileName = item.GetText()
            files.append(str(fileName))
            index = self.remoteList.GetNextSelected(index)
        print "Files to delete: ", files
        self.DeleteRemoteFiles(files)


    def SendSelectedFilesToPlayer(self, event=None):
        index = self.localList.GetFirstSelected()
        localSelection = self.GetLocalSelectionInfo()
        files = localSelection['files']
        print "Files to send: ", files

        # optimize the files before sending them
        # create temp directory
        tmpPath = BASE_PATH + '/' + 'tmp'
        try:
            os.makedirs(tmpPath)
        except OSError as exception:
            print "Exception in creating DIR: ",exception
        rmutil.ImageUtil.OptimizeImages(files, self.path, tmpPath,1920,1080,HOST_SYS == HOST_WIN)
        network.tcpfileclient.sendFiles(files, tmpPath, self.host, self, HOST_SYS == HOST_WIN)
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
        self.LoadRemoteFileList()

    def SetPreviewImage(self, imagePath):
        self._SetPreview('img/clear.png')
        self._SetPreview(imagePath)

    def _SetPreview(self, imagePath):
        #print "PREVIEW IMAGE PATH: " + imagePath
        path = resource_path(imagePath)
        #print "RESOURCE PATH: " + path
        img = wx.Image(path)
        # scale the image, preserving the aspect ratio
        W = img.GetWidth()
        H = img.GetHeight()

        maxSize = 200

        if W > H:
            NewW = maxSize
            NewH = maxSize * H / W
        else:
            NewH = maxSize
            NewW = maxSize * W / H
        img = img.Scale(NewW,NewH)

        self.imageCtrl.SetBitmap(wx.BitmapFromImage(img))

    def LocalFileDoubleClicked(self, event):
        fileName = event.GetText()
        filePath = self.path + '/' +  fileName
        # print "File: ", filePath
        if event.GetText() == '..':
            # directory up
            self.ShowParentDirectory()
        elif os.path.isdir(filePath):
            # open directory
            self.ShowDirectory(filePath)
        else:
            # dialog to verify sending file to player
            msg = "Send file '" + fileName + "' to the player? Stop and restart player when the process is complete!"
            dlg = wx.MessageDialog(self, msg, "Send file to Player", wx.YES_NO | wx.ICON_QUESTION)
            if dlg.ShowModal() == wx.ID_YES:
                self.SendSelectedFilesToPlayer()
            if HOST_SYS == HOST_WIN:
                dlg.Destroy()


    def RemoteFileDoubleClicked(self, event):
        fileName = event.GetText()
        self.DeleteRemoteFile(fileName)

    def DeleteRemoteFile(self, fileName):
        files = [str(fileName)]
        self.DeleteRemoteFiles(files)

    def DeleteRemoteFiles(self, files):
        # dialog to verify deleting file on player
        msg = "Delete the selected file(s) from the player (will stop and restart player)? This can not be undone!"
        dlg = wx.MessageDialog(self, msg, "Delete file(s) from player?", wx.YES_NO | wx.ICON_EXCLAMATION)
        if dlg.ShowModal() == wx.ID_YES:
            dlgStyle =  wx.PD_SMOOTH
            prgDialog = wx.ProgressDialog("Deleting file(s)...", "Deleting file(s) from player...", parent = self, style = dlgStyle)
            prgDialog.Pulse()
            args = ["-i", str(len(files))]
            for file in files:
                args.append("-s")
                args.append(file)
            msgData = network.messages.getMessage(DELETE_FILE, args)
            network.udpconnector.sendMessage(msgData, self.host)
            time.sleep(2)
            wx.CallAfter(prgDialog.Destroy)
            print "Delete timeout passed, initiating data load..."
            self.LoadData()
            #self.LoadRemoteFileList()

    def CheckboxToggled(self, event):
        checkbox = event.GetEventObject()
        print checkbox.GetName()
        msgData = network.messages.getConfigUpdateMessage(checkbox.GetName(), checkbox.IsChecked())
        network.udpconnector.sendMessage(msgData, self.host)

    def ChangeDir(self, event):
        dlg = wx.DirDialog(self, message="Select a directory that contains images or videos you would like to browse and upload to your media player.", defaultPath=self.path, style=wx.DD_CHANGE_DIR)

        # Call the dialog as a model-dialog so we're required to choose Ok or Cancel
        if dlg.ShowModal() == wx.ID_OK:
            # User has selected something, get the path
            filename = dlg.GetPath()
            print "Changing local list to new path: " + filename
            self.ShowDirectory(filename)
        dlg.Destroy()

    def ShowDirectory(self, newPath):
        if not self.path == newPath:
            self.path = newPath
            self.SetPreviewImage('img/preview.png')
            self.UpdateLocalFiles()

    def ShowParentDirectory(self, event=None):
        parent = os.path.abspath(os.path.join(self.path, os.pardir))
        self.ShowDirectory(parent)

    def LoadRemoteFileList(self, event=None):
        if not self.pageDataLoading:
            Publisher.subscribe(self.InsertReceivedFileList, 'remote_files')
            Publisher.subscribe(self.UdpListenerStopped, 'listener_stop')
        #network.udpresponselistener.registerObserver([OBS_FILE_LIST, self.InsertReceivedFileList])
        #network.udpresponselistener.registerObserver([OBS_STOP, self.UdpListenerStopped])
        msgData = network.messages.getMessage(FILELIST_REQUEST)
        dlgStyle =  wx.PD_AUTO_HIDE
        #self.prgDialog = wx.ProgressDialog("Loading...", "Loading filelist from player...", maximum = 1, parent = self.parent, style = dlgStyle)
        #self.prgDialog.Pulse()
        self.remoteListLoading = True
        #self.parent.prgDialog.Pulse("Loading filelist...")
        network.udpconnector.sendMessage(msgData, self.host)

    def LoadRemoteConfig(self, event=None):
        print "Entering LoadRemoteConfig routine...."
        if not self.pageDataLoading:
            Publisher.subscribe(self.UpdateConfigUI, 'config')
            Publisher.subscribe(self.UdpListenerStopped, 'listener_stop')
        #network.udpresponselistener.registerObserver([OBS_CONFIG, self.UpdateConfigUI])
        #network.udpresponselistener.registerObserver([OBS_STOP, self.UdpListenerStopped])
        print "Observers registered..."
        msgData = network.messages.getMessage(CONFIG_REQUEST)
        dlgStyle =  wx.PD_AUTO_HIDE
        #self.prgDialog = wx.ProgressDialog("Loading...", "Loading configuration from player...", maximum = 0, parent = self, style = dlgStyle)
        #self.prgDialog.Pulse()
        self.remoteListLoading = False
        #self.parent.prgDialog.Pulse("Loading configuration...")
        network.udpconnector.sendMessage(msgData, self.host)

    def UdpListenerStopped(self):
        print "UDP LISTENER STOPPED IN PANEL %d" % self.index
        global HOST_SYS
        if self.pageDataLoading:
            if self.remoteListLoading:
                self.pageDataLoading = False
                Publisher.unsubAll()
                if self.parent.prgDialog:
                    print "CLOSING PRG DIALOG IN PARENT..."
                    self.parent.prgDialog.Update(100)
                    if HOST_SYS == HOST_WIN:
                        self.parent.prgDialog.Destroy()
                if self.prgDialog:
                    print "CLOSING PRG DIALOG IN PANEL..."
                    self.prgDialog.Update(100)
                    if HOST_SYS == HOST_WIN:
                        self.prgDialog.Destroy()
            else:
                self.LoadRemoteFileList()
        else:
            if self.prgDialog:
                self.prgDialog.Update(100)
                if HOST_SYS == HOST_WIN:
                    self.prgDialog.Destroy()

    def ButtonClicked(self, event):
        button = event.GetEventObject()
        if button.GetName() == 'btn_identify':
            msgData = network.messages.getMessage(PLAYER_IDENTIFY)
            network.udpconnector.sendMessage(msgData, self.host)
            msg = "The current player will show a test image. Close this dialog to exit identifier mode."
            dlg = wx.MessageDialog(self, msg, "Identifying player", wx.OK | wx.ICON_EXCLAMATION)
            if dlg.ShowModal() == wx.ID_OK:
                msgData2 = network.messages.getMessage(PLAYER_IDENTIFY_DONE)
                network.udpconnector.sendMessage(msgData2, self.host)
            dlg.Destroy()
        elif button.GetName() == 'btn_reboot':
            self.RebootPlayer()

    def RebootPlayer(self):
        self.prgDialog = wx.ProgressDialog("Rebooting...", wordwrap("Player rebooting, this can take up to 1 minute. This dialog will close when the reboot is complete, you may close it manually if you see your player up and running again.", 350, wx.ClientDC(self)), parent = self)
        Publisher.subscribe(self.RebootComplete, "boot_complete")
        #Publisher.subscribe(self.UdpListenerStopped, 'listener_stop')
        self.prgDialog.Pulse()

        msgData = network.messages.getMessage(PLAYER_REBOOT)
        network.udpconnector.sendMessage(msgData, self.host, UDP_REBOOT_TIMEOUT)

    def RebootComplete(self):
        print "REBOOT COMPLETE CALLBACK"
        self.prgDialog.Update(100)
        if HOST_SYS == HOST_WIN:
            self.prgDialog.Destroy()
        dlg = wx.MessageDialog(self,"Reboot complete!","",style=wx.OK)
        dlg.Show()
        if HOST_SYS == HOST_WIN:
            dlg.Destroy()

    def OnPlayerUpdated(self, result):
        self.prgDialog.Destroy()
        dlg = wx.MessageDialog(self,str(result),"Player Update",style=wx.OK)


    def PlayClicked(self, event):
        msgData = network.messages.getMessage(PLAYER_START)
        network.udpconnector.sendMessage(msgData, self.host)

    def StopClicked(self, event):
        msgData = network.messages.getMessage(PLAYER_STOP)
        network.udpconnector.sendMessage(msgData, self.host)



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
