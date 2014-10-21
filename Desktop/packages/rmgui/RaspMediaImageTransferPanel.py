import packages.rmnetwork as network
import packages.rmutil as util
from packages.rmgui import *
from packages.rmgui import ScrollableSelectableImageView as imgView
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
# RASP MEDIA IMAGE TRANSFER PANEL ##############################################
################################################################################
class RaspMediaImageTransferPanel(wx.Panel):
    def __init__(self,parent,id,title,index,host,host_sys):
        wx.Panel.__init__(self,parent,-1)
        global HOST_SYS, BASE_PATH
        HOST_SYS = host_sys
        BASE_PATH = parent.parent.base_path
        self.parent = parent
        self.index = index
        self.host = host
        self.path = self.DefaultPath()
        self.config = []
        self.invalidate = True
        self.remImages = {}
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.notebook_event = None
        self.prgDialog = None
        self.Initialize()
        self.UpdateLocalFiles(False)
        self.UpdatePathLabel()

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

    def Initialize(self):
        # play/stop controls
        pImg = wx.Image(resource_path("img/ic_play.png"), wx.BITMAP_TYPE_PNG).Rescale(20,20,wx.IMAGE_QUALITY_HIGH)
        sImg = wx.Image(resource_path("img/ic_stop.png"), wx.BITMAP_TYPE_PNG).Rescale(20,20,wx.IMAGE_QUALITY_HIGH)
        pBitMap = pImg.ConvertToBitmap()
        sBitMap = sImg.ConvertToBitmap()

        playBtn = wx.BitmapButton(self,-1,pBitMap)
        stopBtn = wx.BitmapButton(self,-1,sBitMap)

        # image views
        nums = self.host.split(".")
        id = 0
        for num in nums:
            id += int(num)
        self.localImg = imgView.ScrollableSelectableImageView(self,id,(300,400),execPath=BASE_PATH)
        self.remoteImg = imgView.ScrollableSelectableImageView(self,id+1,(300,400),deletion=True,execPath=BASE_PATH)

        self.selDir = wx.Button(self,-1,label=tr("select_dir"), size=(300,25))


        # select all/none bitmap buttons
        aImg = wx.Image(resource_path("img/ic_selectall.png"), wx.BITMAP_TYPE_PNG).Rescale(42,18,wx.IMAGE_QUALITY_HIGH)
        nImg = wx.Image(resource_path("img/ic_selectnone.png"), wx.BITMAP_TYPE_PNG).Rescale(42,18,wx.IMAGE_QUALITY_HIGH)
        aBitMap = aImg.ConvertToBitmap()
        nBitMap = nImg.ConvertToBitmap()

        selAllLocal = wx.BitmapButton(self,-1,aBitMap,pos=(0,0))
        clearLocalSel = wx.BitmapButton(self,-1,nBitMap,pos=(0,0))
        selAllRemote = wx.BitmapButton(self,-1,aBitMap,pos=(0,0))
        clearRemoteSel = wx.BitmapButton(self,-1,nBitMap,pos=(0,0))

        # detect USB and backup button
        usbBtn = wx.Button(self,-1,label="Detect USB")
        backupBtn = wx.Button(self,-1,label="Backup Images")

        execute = wx.Button(self,-1,label=tr("apply"), size=(145,25))
        exitBtn = wx.Button(self,-1,label=tr("exit"), size=(145,25))

        # bind buttons
        self.selDir.Bind(wx.EVT_BUTTON, self.ChangeDir)
        selAllLocal.Bind(wx.EVT_BUTTON, self.localImg.SelectAll)
        clearLocalSel.Bind(wx.EVT_BUTTON, self.localImg.UnselectAll)
        usbBtn.Bind(wx.EVT_BUTTON, self.WaitForUSB)
        selAllRemote.Bind(wx.EVT_BUTTON, self.remoteImg.SelectAll)
        clearRemoteSel.Bind(wx.EVT_BUTTON, self.remoteImg.UnselectAll)
        backupBtn.Bind(wx.EVT_BUTTON, self.BackupPlayerFiles)
        playBtn.Bind(wx.EVT_BUTTON, self.Play)
        stopBtn.Bind(wx.EVT_BUTTON, self.Stop)
        execute.Bind(wx.EVT_BUTTON, self.ExecuteChanges)
        exitBtn.Bind(wx.EVT_BUTTON, self.parent.parent.Close)

        # divider lines
        line = wx.StaticLine(self,-1,size=(652,2))
        lineV1 = wx.StaticLine(self,-1,size=(2,400), style=wx.VERTICAL)

        # add elements to UI
        self.mainSizer.Add(self.selDir, flag=wx.LEFT|wx.TOP, border=10)
        imgSizer = wx.BoxSizer()
        # left image selection section
        imgLeftSizer = wx.BoxSizer(wx.VERTICAL)
        imgLeftSizer.Add(self.localImg)
        leftBtnSizer = wx.BoxSizer()
        leftBtnSizer.Add(selAllLocal)
        leftBtnSizer.Add(clearLocalSel)
        leftBtnSizer.Add(usbBtn, flag=wx.ALIGN_CENTER_VERTICAL)
        imgLeftSizer.Add(leftBtnSizer)
        # right image selection section
        imgRightSizer = wx.BoxSizer(wx.VERTICAL)
        imgRightSizer.Add(self.remoteImg)
        rightBtnSizer = wx.BoxSizer()
        rightBtnSizer.Add(selAllRemote)
        rightBtnSizer.Add(clearRemoteSel)
        rightBtnSizer.Add(backupBtn, flag=wx.ALIGN_CENTER_VERTICAL)
        imgRightSizer.Add(rightBtnSizer)
        imgSizer.Add(imgLeftSizer,flag=wx.RIGHT,border=10)
        imgSizer.Add(lineV1, flag=wx.LEFT|wx.RIGHT, border=5)
        imgSizer.Add(imgRightSizer, flag=wx.LEFT, border=10)
        self.mainSizer.Add(imgSizer, flag=wx.LEFT|wx.RIGHT, border=10)
        self.mainSizer.Add(line, flag=wx.TOP|wx.BOTTOM, border=5)
        botSizer = wx.BoxSizer()
        botSizer.Add(stopBtn)
        botSizer.Add(playBtn, flag=wx.RIGHT, border=280)
        botSizer.Add(exitBtn, flag=wx.ALL, border=3)
        botSizer.Add(execute, flag=wx.ALL, border=3)
        self.mainSizer.Add(botSizer, flag=wx.ALL|wx.ALIGN_RIGHT, border=10)

        self.SetSizerAndFit(self.mainSizer)
        self.Show(True)

    def WaitForUSB(self, event=None):
        print "Waiting for USB Drive..."
        Publisher.subscribe(self.USBConnected, 'usb_connected')
        self.prgDialog = wx.ProgressDialog(tr("loading"), tr("plug_usb"))
        self.prgDialog.Pulse()
        if HOST_SYS == HOST_WIN:
            util.Win32DeviceDetector.waitForUSBDrive()
        elif HOST_SYS == HOST_MAC or HOST_SYS == HOST_LINUX:
            util.UnixDriveDetector.waitForUSBDrive()


    def USBConnected(self, path):
        # Publisher.unsubscribe(self.USBConnected, 'usb_connected')
        # print "USB Drive connected and mounted in path %s" % path
        time.sleep(2)
        self.prgDialog.Update(100)
        if HOST_SYS == HOST_WIN:
            # add colon as path is only the drive letter of the connected USB drive
            path += ":"
            self.prgDialog.Destroy()

        self.ShowDirectory(path)

    def ExecuteChanges(self, event):
        delFiles = self.remoteImg.GetSelection()
        newFiles = self.localImg.GetSelection()

        # execute changes
        if len(delFiles) > 0:
            self.DeleteRemoteFiles(delFiles)
        if len(newFiles) > 0:
            self.SendFilesToPlayer(newFiles)

        # reload data
        self.invalidate = True
        self.LoadData()

    def SetHost(self, hostAddress):
        self.host = hostAddress

    def LoadData(self):
        if self.invalidate:
            self.LoadRemoteFiles()
        else:
            self.UpdateRemoteFiles(self.remImages[self.host])
        self.LoadRemoteConfig()
        self.LayoutAndFit()

    def LoadRemoteFiles(self, event=None):
        # remove previous listener that may be present from other tab
        Publisher.unsubAll()
        # send udp request to receive files over tcp
        Publisher.subscribe(self.UpdateRemoteFiles, 'remote_files_loaded')
        msgData = network.messages.getMessage(FILE_DATA_REQUEST)
        network.udpconnector.sendMessage(msgData, self.host)
        # open tcp socket for file transmission
        network.tcpfilesocket.openFileSocket(self, HOST_SYS == HOST_WIN)
        self.invalidate = False

    def LoadRemoteConfig(self):
        Publisher.subscribe(self.UpdateRemoteConfig, 'config')
        msgData = network.messages.getMessage(CONFIG_REQUEST)
        network.udpconnector.sendMessage(msgData, self.host)

    def UpdateRemoteConfig(self, config, isDict=False):
        if isDict:
            configDict = config
        else:
            configDict = ast.literal_eval(config)
        self.config = configDict

    def UdpListenerStopped(self):
        # print "UDP LISTENER STOPPED IN PANEL %d" % self.index
        global HOST_SYS
        Publisher.unsubAll()
        if self.prgDialog:
            self.prgDialog.Update(100)
            if HOST_SYS == HOST_WIN:
                self.prgDialog.Destroy()

    def UpdatePathLabel(self):
        txt = self.path
        if len(self.path) > 25:
            txt = '/'
            words = self.path.split("/")
            for word in reversed(words):
                if len(txt) < 25:
                    txt = '/' + word + txt
            txt = "..." + txt
            if len(txt) > 39:
                txt = "..." + txt[-36:]
        self.selDir.SetLabel(txt)

    def UpdateLocalFiles(self, layout=True):
        dirFiles = os.listdir(self.path)
        images = []
        for file in dirFiles:
            if not file.startswith(".") and file.endswith((SUPPORTED_IMAGE_EXTENSIONS)):
                images.append({"img_name": file, "img_path": self.path + '/', "checked": False})
        self.localImg.UpdateImages(images)
        if layout:
            self.LayoutAndFit()

    def UpdateRemoteFiles(self, files):
        self.remImages[self.host] = files
        self.remoteImg.UpdateImages(files)

        # unselect all local images when remote images are updated
        self.localImg.UnselectAll()
        self.LayoutAndFit()


    def LayoutAndFit(self):
        self.mainSizer.Layout()
        self.Fit()
        self.parent.Fit()
        self.parent.parent.Fit()
        self.parent.parent.Center()


    def SendFilesToPlayer(self, files):
        # optimize the files before sending them
        # create temp directory
        from os.path import expanduser
        home = expanduser("~")
        appPath = home + '/.raspmedia/'
        tmpRoot = appPath + 'tmp/'
        tmpPath = tmpRoot + 'opt_tmp/'
        if not os.path.isdir(appPath):
            os.mkdir(appPath)
        if not os.path.isdir(tmpRoot):
            os.mkdir(tmpRoot)
        if not os.path.isdir(tmpPath):
            os.mkdir(tmpPath)

        util.ImageUtil.OptimizeImages(files, self.path, tmpPath,1920,1080,HOST_SYS == HOST_WIN)
        network.tcpfileclient.sendFiles(files, tmpPath, self.host, self, HOST_SYS == HOST_WIN)
        shutil.rmtree(tmpPath)
        dlg = wx.ProgressDialog(tr("saving"), tr("saving_files_player"), style = wx.PD_AUTO_HIDE)
        dlg.Pulse()
        numFiles = len(files)
        # give the player some time per file to save and create a thumbnail
        time.sleep(numFiles * 0.5)
        dlg.Update(100)
        if HOST_SYS == HOST_WIN:
            dlg.Destroy()

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

    def ChangeDir(self, event):
        dlg = wx.DirDialog(self, message=tr("select_file_dir"), defaultPath=self.path, style=wx.DD_CHANGE_DIR)

        # Call the dialog as a model-dialog so we're required to choose Ok or Cancel
        if dlg.ShowModal() == wx.ID_OK:
            # User has selected something, get the path
            filename = dlg.GetPath()
            self.ShowDirectory(filename)
        dlg.Destroy()

    def BackupPlayerFiles(self, event):
        dlg = wx.DirDialog(self, message=tr("select_backup_dir"), defaultPath=self.path, style=wx.DD_CHANGE_DIR)

        # Call the dialog as a model-dialog so we're required to choose Ok or Cancel
        if dlg.ShowModal() == wx.ID_OK:
            # User has selected something, get the path
            filename = dlg.GetPath()
            print "Saving files to ", filename
        dlg.Destroy()

    def Play(self, event=None):
        msgData = network.messages.getMessage(PLAYER_START)
        network.udpconnector.sendMessage(msgData, self.host)

    def Stop(self, event=None):
        msgData = network.messages.getMessage(PLAYER_STOP)
        network.udpconnector.sendMessage(msgData, self.host)

    def ShowDirectory(self, newPath):
        if not self.path == newPath:
            self.path = newPath
            self.UpdatePathLabel()
            self.UpdateLocalFiles()

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
