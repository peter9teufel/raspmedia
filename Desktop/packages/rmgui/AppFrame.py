import wx
import RemoteNotebook as remote
import SettingsFrame as prefs
import WifiDialog as wifi
import packages.rmnetwork as network
from packages.lang.Localizer import *
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

        # Create an accelerator table
        sc_wifi_id = wx.NewId()
        sc_settings_id = wx.NewId()
        self.Bind(wx.EVT_MENU, self.ShowPlayerSettings, id=sc_settings_id)
        self.Bind(wx.EVT_MENU, self.ShowWifiSettings, id=sc_wifi_id)

        self.accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord(','), sc_settings_id),
                                              (wx.ACCEL_SHIFT, ord('W'), sc_wifi_id)
                                             ])
        self.SetAcceleratorTable(self.accel_tbl)

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
        menuSettings = fileMenu.Append(wx.ID_ANY, "&"+tr("player_settings") + "\tCTRL+,", tr("player_settings"))
        menuSettings.SetBitmap(wx.Bitmap('img/tools.png'))
        menuExit = fileMenu.Append(wx.ID_EXIT, "&"+tr("exit"),tr("exit"))
        self.Bind(wx.EVT_MENU, self.Close, menuExit)
        self.Bind(wx.EVT_MENU, self.ShowPlayerSettings, menuSettings)

        # Help Menu
        about = helpMenu.Append(wx.ID_ANY, "&"+tr("about"))
        self.Bind(wx.EVT_MENU, self.ShowAbout, about)

        # Menubar
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&"+tr("file")) # Adding the "filemenu" to the MenuBar

        menuBar.Append(helpMenu, "&"+tr("about"))
        self.SetMenuBar(menuBar)

    def ShowAbout(self, event):
        # message read from defined version info file in the future
        msg = "RaspMedia Control v1.0\n(c) 2014 by www.multimedia-installationen.at\nContact: software@multimedia-installationen.at\nAll rights reserved."
        dlg = wx.MessageDialog(self, msg, "About", style=wx.OK)
        dlg.ShowModal()

    def ShowPlayerSettings(self, event):
        settings = prefs.SettingsFrame(self,-1,tr("player_settings"),self.notebook.CurrentlyActiveHost(), self.notebook.CurrentConfig())
        settings.Center()
        settings.SetBackgroundColour('WHITE')
        settings.Refresh()
        settings.Show()

    def ShowWifiSettings(self, event):
        host = self.notebook.CurrentlyActiveHost()
        wifiDlg = wifi.WifiDialog(self, -1, tr("wifi_settings"), host["addr"])
        wifiDlg.ShowModal()

    def SettingsClosedWithConfig(self, config):
        self.notebook.UpdateCurrentPlayerUI(config)
