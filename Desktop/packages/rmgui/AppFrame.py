import wx
import RemoteNotebook as remote
import SettingsFrame as prefs
import packages.rmnetwork as network
import sys
from wx.lib.pubsub import pub as Publisher
from wx.lib.wordwrap import wordwrap

################################################################################
# MAIN FRAME OF APPLICATION ####################################################
################################################################################
class AppFrame(wx.Frame):
    def __init__(self,parent,id,title,base_path):
        wx.Frame.__init__(self,parent,id,title,size=(600,600))
        self.parent = parent
        self.base_path = base_path
        self.Bind(wx.EVT_CLOSE, self.Close)
        self.SetupMenuBar()
        print "Initializing Notebook..."
        self.notebook = remote.RemoteNotebook(self,-1,None)
        print "Showing window..."
        self.Center()
        self.Show()
        print "Starting host search..."
        self.notebook.SearchHosts()

    def Close(self, event=None):
        Publisher.unsubAll()
        self.notebook.Close()
        network.udpresponselistener.destroy()
        self.Destroy()
        sys.exit(0)

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

    def ShowAbout(self, event):
        # message read from defined version info file in the future
        msg = "RaspMedia Control v1.0\n(c) 2014 by www.multimedia-installationen.at\nContact: software@multimedia-installationen.at\nAll rights reserved."
        dlg = wx.MessageDialog(self, msg, "About", style=wx.OK)
        dlg.ShowModal()

    def ShowPlayerSettings(self, event):
        settings = prefs.SettingsFrame(self,-1,"Player Settings",self.notebook.CurrentlyActiveHost(), self.notebook.CurrentConfig())
        settings.Center()
        settings.SetBackgroundColour('WHITE')
        settings.Refresh()
        settings.Show()

    def SettingsClosedWithConfig(self, config):
        self.notebook.UpdateCurrentPlayerUI(config)
