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
        self.mainSizer = wx.GridBagSizer()
        self.notebook_event = None
        self.prgDialog = None
        self.Initialize()

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
        # TODO INIT UI

        # fit size and show
        self.Fit()
        self.parent.Fit()
        self.parent.parent.Fit()
        self.Show(True)

    def PageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.parent.GetSelection()
        self.notebook_event = event
        # print "OnPageChanged, old:%d, new:%d, sel:%d" % (old, new, sel)
        newPage = self.parent.GetPage(new)
        if self.index == newPage.index:
            self.LoadData()

    def SetHost(self, hostAddress):
        self.host = hostAddress

    def LoadData(self):
        # TODO CHANGE DIALOG MESSAGE FOR FILE LOADING
        #self.prgDialog = wx.ProgressDialog(tr("loading"), tr("msg_loading_config_filelist"))
        #self.prgDialog.Pulse()
        #self.LoadRemoteFiles()
        pass

    def LoadRemoteFiles(self, event=None):
        # TODO modify routine to a new FILE_DATA_REQUEST

        if not self.pageDataLoading:
            Publisher.subscribe(self.UpdateRemoteFiles, 'remote_files_loaded')
        msgData = network.messages.getMessage(FILELIST_REQUEST)
        dlgStyle =  wx.PD_AUTO_HIDE
        self.remoteListLoading = True
        network.udpconnector.sendMessage(msgData, self.host)

    def UdpListenerStopped(self):
        # print "UDP LISTENER STOPPED IN PANEL %d" % self.index
        global HOST_SYS
        Publisher.unsubAll()
        if self.prgDialog:
            self.prgDialog.Update(100)
            if HOST_SYS == HOST_WIN:
                self.prgDialog.Destroy()

    def UpdateLocalFiles(self):
        #TODO update scrollable selectable image view with local files
        pass

    def UpdateRemoteFiles(self):
        #TODO update scrollable selectable image view with remote files
        pass

    def DeleteSelectedRemoteFile(self, event):
        # TODO get selected remote filenames of files to delete from player to variable 'files'

        self.DeleteRemoteFiles(files)


    def SendSelectedFilesToPlayer(self, event=None):
        # TODO get selected local filenames and save them to variable 'files'

        # optimize the files before sending them
        # create temp directory
        tmpPath = BASE_PATH + '/' + 'tmp'
        try:
            os.makedirs(tmpPath)
        except OSError as exception:
            print "Exception in creating DIR: ",exception
        rmutil.ImageUtil.OptimizeImages(files, self.path, tmpPath,1920,1080,HOST_SYS == HOST_WIN)
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

        # TODO UPDATE UI

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
            self.LoadData()

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
