import packages.rmnetwork as network
import packages.rmutil as rmutil
from packages.rmgui import *
from packages.rmnetwork.constants import *
from packages.lang.Localizer import *
import os, sys, platform, ast, time, threading, shutil

import wx
if platform.system() == "Linux":
    from wx.lib.pubsub import setupkwargs
    from wx.lib.pubsub import pub as Publisher
else:
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
        self.playerSizer = wx.BoxSizer()
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
        self.prgDialog = wx.ProgressDialog(tr("loading"), tr("msg_loading_config_filelist"))
        self.prgDialog.Pulse()
        self.LoadRemoteConfig()

    def PageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.parent.GetSelection()
        self.notebook_event = event
        # print "OnPageChanged, old:%d, new:%d, sel:%d" % (old, new, sel)
        newPage = self.parent.GetPage(new)
        if self.index == newPage.index:
            # print "PAGE CHANGED TO INDEX %d - PROCESSING AND LOADING DATA..." % (self.index)
            self.pageDataLoading = True
            self.LoadData()

    def Initialize(self):
        self.SetupPlayerSection()
        self.SetupFileLists()

        self.mainSizer.Add(self.playerSizer,(0,0), flag = wx.LEFT | wx.RIGHT, border=10)
        self.mainSizer.Add(self.filesSizer, (2,0), flag=wx.BOTTOM | wx.LEFT | wx.RIGHT, border=10)

        self.SetSizerAndFit(self.mainSizer)

        line = wx.StaticLine(self,-1,size=(self.mainSizer.GetSize()[0],2))
        self.mainSizer.Add(line, (1,0), flag = wx.TOP | wx.BOTTOM, border = 10)

        #self.Fit()
        #self.parent.Fit()
        #self.parent.parent.Fit()
        self.LayoutAndFit()
        self.Show(True)

    def LayoutAndFit(self):
        self.mainSizer.Layout()
        self.Fit()
        self.parent.Fit()
        self.parent.parent.Fit()
        self.parent.parent.Center()

    def SetupPlayerSection(self):
        playerBox = wx.StaticBox(self,-1,label="Player Info")
        playerBoxSizer = wx.StaticBoxSizer(playerBox, wx.VERTICAL)

        # player name and address
        nameSizer = wx.BoxSizer()
        nameLabel = wx.StaticText(self,-1,label=tr("player_name")+": ")
        self.playerNameLabel = wx.StaticText(self,-1,label="", size = (130,nameLabel.GetSize()[1]))
        nameSizer.Add(nameLabel)
        nameSizer.Add(self.playerNameLabel)

        addrSizer = wx.BoxSizer()
        addrLabel = wx.StaticText(self,-1,label=tr("ip_address")+": ")
        playerAddr = wx.StaticText(self,-1,label=self.host)
        addrSizer.Add(addrLabel)
        addrSizer.Add(playerAddr)

        playerBoxSizer.Add(nameSizer,flag=wx.ALL,border=5)
        playerBoxSizer.Add(addrSizer,flag=wx.ALL,border=5)

        # Play and Stop Button
        ctrlBox = wx.StaticBox(self,-1,label=tr("remote_control"))
        ctrlSizer = wx.StaticBoxSizer(ctrlBox, wx.VERTICAL)

        play = wx.Button(self,-1,label=tr("play"))
        stop = wx.Button(self,-1,label=tr("stop"))
        identify = wx.Button(self,-1,label=tr("identify"))
        identify.SetName("btn_identify")
        reboot = wx.Button(self,-1,label=tr("reboot"), size = identify.GetSize())
        reboot.SetName("btn_reboot")

        self.Bind(wx.EVT_BUTTON, self.PlayClicked, play)
        self.Bind(wx.EVT_BUTTON, self.StopClicked, stop)
        self.Bind(wx.EVT_BUTTON, self.ButtonClicked, identify)
        self.Bind(wx.EVT_BUTTON, self.ButtonClicked, reboot)

        btnSizer = wx.GridBagSizer()

        btnSizer.Add(play,(0,0),flag=wx.LEFT|wx.TOP,border=5)
        btnSizer.Add(stop,(1,0),flag=wx.LEFT|wx.BOTTOM,border=5)
        btnSizer.Add(identify,(0,1),flag=wx.ALL,border=5)
        btnSizer.Add(reboot,(1,1),flag=wx.LEFT|wx.RIGHT|wx.BOTTOM,border=5)
        ctrlSizer.Add(btnSizer)

        # add to player sizer
        self.playerSizer.Add(playerBoxSizer)
        self.playerSizer.Add(ctrlSizer,flag=wx.LEFT,border=15)

    def SetupFileLists(self):
        self.filesSizer.SetEmptyCellSize((0,0))
        # setup file lists and image preview
        self.AddLocalList()
        self.AddImagePreview()
        self.AddRemoteList()

        selectFolder = wx.Button(self,-1,label=tr("select_dir"))
        self.filesSizer.Add(selectFolder, (0,0), flag = wx.TOP | wx.BOTTOM, border = 5)
        self.Bind(wx.EVT_BUTTON, self.ChangeDir, selectFolder)

        button = wx.Button(self,-1,label=tr("refresh_remote_filelist"))
        self.filesSizer.Add(button,(4,0))
        self.Bind(wx.EVT_BUTTON, self.LoadRemoteFileList, button)
        self.filesSizer.Fit(self)

    def AddLocalList(self):
        # print "Initializing empty local lists..."
        self.localList = wx.ListCtrl(self,-1,size=(400,220),style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        # print "Showing list..."
        self.localList.Show(True)
        self.localList.InsertColumn(0,tr("filename"), width = 300)
        self.localList.InsertColumn(1,tr("filesize"), width = 80, format = wx.LIST_FORMAT_RIGHT)
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
        # print "Initializing empty remote lists..."
        self.remoteList=wx.ListCtrl(self,-1,size=(600,200),style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.remoteList.Show(True)
        self.remoteList.InsertColumn(0,tr("remote_files")+": ", width = 598)
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
            size = (os.stat(self.path + '/' + file).st_size)
            if not file.startswith(('$','.')):
                if file.endswith((SUPPORTED_IMAGE_EXTENSIONS)):
                    files.append({"filename": file, "size": os.stat(self.path + '/' + file).st_size})
                elif file.endswith((SUPPORTED_VIDEO_EXTENSIONS)): #and size < MAX_FILESIZE_TCP:
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

    def InsertReceivedFileList(self, serverAddr, files):
        # print "UPDATING REMOTE FILELIST UI..."
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
        # print configDict
        self.config = configDict
        self.playerNameLabel.SetLabel(configDict['player_name'])
        #if self.notebook_event:
        #	self.parent.SetPageText(self.notebook_event.GetSelection(), str(configDict['player_name']))
        #else:
        self.parent.SetPageText(self.index, str(configDict['player_name']))
        self.parent.parent.Refresh()

    def GetLocalSelectionInfo(self):
        mixed = False
        prevType = None
        curType = None
        index = self.localList.GetFirstSelected()
        cnt = 0
        files = []
        while not index == -1:
            item = self.localList.GetItem(index,0)
            name = item.GetText()
            files.append(name)
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
                selLabel = "%d %s" % (len(files),tr("mediafiles_selected"))
            elif sel['type'] == 'dir':
                selLabel = tr("multiple_dir_selected")
            else:
                selLabel = "%d %s" % (len(files),tr("mixed_selected"))
        return selLabel

    def LocalFileRightClicked(self, event):
        global HOST_SYS
        file = event.GetText()
        menu = wx.Menu()
        if file == '..' or os.path.isdir(self.path + '/' + file):
            item = menu.Append(wx.NewId(), tr("open"))
            self.Bind(wx.EVT_MENU, self.ShowSelectedDirectory, item)
        else:
            item = menu.Append(wx.NewId(), tr("send_to_player"))
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
        item = menu.Append(wx.NewId(), tr("delete"))
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
            files.append(fileName)
            index = self.remoteList.GetNextSelected(index)
        # print "Files to delete: ", files
        self.DeleteRemoteFiles(files)


    def SendSelectedFilesToPlayer(self, event=None):
        index = self.localList.GetFirstSelected()
        localSelection = self.GetLocalSelectionInfo()
        files = localSelection['files']
        # print "Files to send: ", files

        # optimize the files before sending them
        # create temp directory
        tmpPath = BASE_PATH + '/' + 'tmp'
        try:
            os.makedirs(tmpPath)
        except OSError as exception:
            print "Exception in creating DIR: ",exception
        images = []
        videos = []
        for f in files:
            if f.endswith((SUPPORTED_IMAGE_EXTENSIONS)):
                images.append(f)
            elif f.endswith((SUPPORTED_VIDEO_EXTENSIONS)):
                videos.append(f)
        if len(images) > 0:
            rmutil.ImageUtil.OptimizeImages(images, self.path, tmpPath,1920,1080,HOST_SYS == HOST_WIN)
        for video in videos:
            shutil.copyfile(self.path + "/" + video, tmpPath + "/" + video)
        network.tcpfileclient.sendFiles(files, tmpPath, self.host, self, HOST_SYS == HOST_WIN)
        # print "Deleting temporary files..."
        shutil.rmtree(tmpPath)
        dlg = wx.ProgressDialog(tr("saving"), tr("saving_files_player"), style = wx.PD_AUTO_HIDE)
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
        ## print "PREVIEW IMAGE PATH: " + imagePath
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
            msg = tr("dlg_msg_send_file_player")
            dlg = wx.MessageDialog(self, msg, tr("dlg_title_send_file_player"), wx.YES_NO | wx.ICON_QUESTION)
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
        msg = tr("dlg_msg_delete_files_player")
        dlg = wx.MessageDialog(self, msg, tr("dlg_title_delete_files_player"), wx.YES_NO | wx.ICON_EXCLAMATION)
        if dlg.ShowModal() == wx.ID_YES:
            dlgStyle =  wx.PD_SMOOTH
            prgDialog = wx.ProgressDialog(tr("deleting"), tr("deleting_files"), parent = self, style = dlgStyle)
            prgDialog.Pulse()
            args = ["-i", str(len(files))]
            for file in files:
                args.append("-s")
                args.append(file)
            msgData = network.messages.getMessage(DELETE_FILE, args)
            network.udpconnector.sendMessage(msgData, self.host)
            time.sleep(2)
            wx.CallAfter(prgDialog.Destroy)
            # print "Delete timeout passed, initiating data load..."
            self.LoadData()
            #self.LoadRemoteFileList()

    def CheckboxToggled(self, event):
        checkbox = event.GetEventObject()
        # print checkbox.GetName()
        msgData = network.messages.getConfigUpdateMessage(checkbox.GetName(), checkbox.IsChecked())
        network.udpconnector.sendMessage(msgData, self.host)

    def ChangeDir(self, event):
        dlg = wx.DirDialog(self, message=tr("select_file_dir"), defaultPath=self.path, style=wx.DD_CHANGE_DIR)

        # Call the dialog as a model-dialog so we're required to choose Ok or Cancel
        if dlg.ShowModal() == wx.ID_OK:
            # User has selected something, get the path
            filename = dlg.GetPath()
            # print "Changing local list to new path: " + filename
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
        msgData = network.messages.getMessage(FILELIST_REQUEST)
        dlgStyle =  wx.PD_AUTO_HIDE
        self.remoteListLoading = True
        network.udpconnector.sendMessage(msgData, self.host)

    def LoadRemoteConfig(self, event=None):
        # print "Entering LoadRemoteConfig routine...."
        if not self.pageDataLoading:
            Publisher.subscribe(self.UpdateConfigUI, 'config')
            Publisher.subscribe(self.UdpListenerStopped, 'listener_stop')
        msgData = network.messages.getMessage(CONFIG_REQUEST)
        dlgStyle =  wx.PD_AUTO_HIDE
        self.remoteListLoading = False
        network.udpconnector.sendMessage(msgData, self.host)

    def UdpListenerStopped(self):
        global HOST_SYS
        if self.pageDataLoading:
            if self.remoteListLoading:
                self.pageDataLoading = False
                if self.parent.prgDialog:
                    self.parent.prgDialog.Update(100)
                    if HOST_SYS == HOST_WIN:
                        self.parent.prgDialog.Destroy()
                if self.prgDialog:
                    self.prgDialog.Update(100)
                    if HOST_SYS == HOST_WIN:
                        self.prgDialog.Destroy()
            else:
                Publisher.unsubscribe(self.UpdateConfigUI, 'config')
                self.LoadRemoteFileList()
        else:
            if self.prgDialog:
                self.prgDialog.Update(100)
                if HOST_SYS == HOST_WIN:
                    self.prgDialog.Destroy()
        self.LayoutAndFit()

    def ButtonClicked(self, event):
        button = event.GetEventObject()
        if button.GetName() == 'btn_identify':
            msgData = network.messages.getMessage(PLAYER_IDENTIFY)
            network.udpconnector.sendMessage(msgData, self.host)
            msg = tr("dlg_msg_identify")
            dlg = wx.MessageDialog(self, msg, tr("dlg_title_identify"), wx.OK | wx.ICON_EXCLAMATION)
            if dlg.ShowModal() == wx.ID_OK:
                msgData2 = network.messages.getMessage(PLAYER_IDENTIFY_DONE)
                network.udpconnector.sendMessage(msgData2, self.host)
            dlg.Destroy()
        elif button.GetName() == 'btn_reboot':
            self.RebootPlayer()

    def RebootPlayer(self):
        self.prgDialog = wx.ProgressDialog(tr("dlg_title_reboot"), wordwrap(tr("dlg_msg_reboot"), 350, wx.ClientDC(self)), parent = self)
        Publisher.subscribe(self.RebootComplete, "boot_complete")
        self.prgDialog.Pulse()

        msgData = network.messages.getMessage(PLAYER_REBOOT)
        network.udpconnector.sendMessage(msgData, self.host, UDP_REBOOT_TIMEOUT)

    def RebootComplete(self):
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
    except Exception:
        base_path = BASE_PATH
    resPath = os.path.normcase(os.path.join(base_path, relative_path))
    #resPath = base_path + relative_path
    #print resPath
    return resPath
