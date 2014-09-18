import wx
import ImageTransferNotebook as imageNotebook
import SettingsFrame as prefs
import WifiDialog as wifi
import packages.rmnetwork as network
from packages.lang.Localizer import *
import sys, os, shutil
if platform.system() == "Linux":
    from wx.lib.pubsub import setupkwargs
    from wx.lib.pubsub import pub as Publisher
else:
    from wx.lib.pubsub import pub as Publisher
from wx.lib.wordwrap import wordwrap

BASE_PATH = None

################################################################################
# MAIN FRAME OF APPLICATION ####################################################
################################################################################
class ImageTransferFrame(wx.Frame):
    def __init__(self,parent,id,title,base_path):
        wx.Frame.__init__(self,parent,id,title,size=(652,585),style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        self.parent = parent
        self.base_path = base_path
        global BASE_PATH
        BASE_PATH = base_path
        self.Bind(wx.EVT_CLOSE, self.Close)
        self.notebook = imageNotebook.ImageTransferNotebook(self,-1,None)

        self.Center()
        self.Show()
        self.notebook.SearchHosts()

    def Close(self, event=None):
        Publisher.unsubAll()
        self.notebook.Close()
        network.udpresponselistener.destroy()
        self.Destroy()
        sys.exit(0)


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
