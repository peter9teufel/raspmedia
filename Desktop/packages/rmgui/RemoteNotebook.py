import packages.rmnetwork as network
import packages.rmutil as rmutil
from packages.rmgui import RaspMediaControlPanel as rmc
from packages.rmnetwork.constants import *
from packages.lang.Localizer import *
import os, sys, platform, ast, time, threading, shutil

import wx
from wx.lib.pubsub import pub as Publisher
from wx.lib.wordwrap import wordwrap
from packages.lang.Localizer import *

playerCount = 0
activePageNr = 0

HOST_WIN = 1
HOST_MAC = 2
HOST_LINUX = 3
HOST_SYS = None

################################################################################
# REMOTE NOTEBOOK FOR PLAYER PANELS ############################################
################################################################################
class RemoteNotebook(wx.Notebook):
    def __init__(self, parent, id, log):
        wx.Notebook.__init__(self, parent, id, style=
                            wx.BK_DEFAULT
                            #wx.BK_TOP
                            #wx.BK_BOTTOM
                            #wx.BK_LEFT
                            #wx.BK_RIGHT
                            # | wx.NB_MULTILINE
                            )
        self.parent = parent
        self.log = log
        self.pages = []
        self.hostSearch = False
        self.hosts = []
        self.activePageNr = 0
        global HOST_SYS
        # check platform
        if platform.system() == 'Windows':
            HOST_SYS = HOST_WIN
        elif platform.system() == 'Darwin':
            HOST_SYS = HOST_MAC
        elif platform.system() == 'Linux':
            HOST_SYS = HOST_LINUX

        if HOST_SYS == HOST_LINUX or HOST_SYS == HOST_WIN:
            self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        elif HOST_SYS == HOST_MAC:
            self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanged)
        self.Show()

    def Close(self):
        self.Destroy()

    def CurrentlyActiveHost(self):
        return self.hosts[self.activePageNr]

    def CurrentConfig(self):
        return self.GetPage(self.activePageNr).config

    def UpdateCurrentPlayerUI(self, config):
        self.GetPage(self.activePageNr).UpdateConfigUI(config, True)

    def HostFound(self, host, playerName):
        global playerCount
        # print "Adding host to list..."
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
        Publisher.subscribe(self.HostFound, 'host_found')
        Publisher.subscribe(self.UdpListenerStopped, 'listener_stop')
        msgData = network.messages.getMessage(SERVER_REQUEST)
        self.prgDialog = wx.ProgressDialog(tr("searching"), tr("searching_players"), parent = self, style = wx.PD_AUTO_HIDE)
        self.prgDialog.Pulse()
        network.udpconnector.sendMessage(msgData)

    def LoadPageData(self, pageNumber):
        # print "Loading config and remote list for page ", pageNumber
        self.GetPage(pageNumber).LoadData()

    def UdpListenerStopped(self):
        global playerCount
        Publisher.unsubscribe(self.UdpListenerStopped, 'listener_stop')
        Publisher.unsubscribe(self.HostFound, 'host_found')
        # print "Number of players found: ", playerCount
        if self.hostSearch:
            self.hostSearch = False
            if playerCount == 0:
                self.prgDialog.Update(100)
                if HOST_SYS == HOST_WIN:
                    self.prgDialog.Destroy()
                dlg = wx.SingleChoiceDialog(self,wordwrap(tr("no_players_found"), 300, wx.ClientDC(self)), tr("no_player"), [tr("rescan"), tr("exit")])
                result = dlg.ShowModal()
                selection = dlg.GetSelection()
                # print "RESULT: ", result
                if result == wx.ID_OK:
                    # print "OK clicked, checking selected index... ", selection
                    if selection == 0: # RESCAN
                        self.SearchHosts()
                    #elif selection == 1:
                    #	pass
                    elif selection == 1: # EXIT
                        self.parent.Close()
                elif result == wx.ID_CANCEL:
                    # print "Cancel clicked, terminating program, bye bye..."
                    self.parent.Close()
            else:
                #self.prgDialog.Destroy()
                ind = 0
                for host in self.hosts:
                    # print "Preparing page for " + host['name']
                    # print "Player address: " + host['addr']
                    curPage = rmc.RaspMediaCtrlPanel(self,-1,host['name'],ind,host['addr'],HOST_SYS)
                    self.pages.append(curPage)
                    self.AddPage(curPage, host['name'])
                    ind += 1
                self.LoadPageData(0)
                self.Fit()
                self.parent.Fit()
                if HOST_SYS == HOST_WIN:
                    self.parent.SetSize((self.GetSize()[0]-85, self.GetSize()[1]+35))
                else:
                    self.parent.SetSize((self.GetSize()[0]-115, self.GetSize()[1]))
                self.parent.Center()

    def OnPageChanged(self, event):
        global HOST_SYS
        # print "ON PAGE CHANGED TRIGGER"
        self.activePageNr = event.GetSelection()
        if HOST_SYS == HOST_LINUX and event.GetOldSelection() == -1:
            pass
        else:
            # pass event to all pages, appropriate one will load data
            for page in self.pages:
                page.PageChanged(event)
