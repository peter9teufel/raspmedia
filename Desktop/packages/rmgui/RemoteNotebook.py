import packages.rmnetwork as network
import packages.rmutil as rmutil
from packages.rmgui import RaspMediaControlPanel as rmc
from packages.rmgui import RaspMediaAllPlayersPanel as rmap
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
from operator import itemgetter
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
        if self.activePageNr < len(self.hosts):
            # page of single player host is active, return host
            return self.hosts[self.activePageNr]
        else:
            # all players tab or group tab is opened, no host to return
            return -1

    def CurrentConfig(self):
        return self.GetPage(self.activePageNr).config

    def GetConfigForHost(self, host):
        for i in range(self.GetPageCount()):
            page = self.GetPage(i)
            pHost = page.host
            if host['addr'] == pHost:
                return page.config
        return -1

    def UpdatePlayerConfig(self, config, host):
        for i in range(self.GetPageCount()):
            page = self.GetPage(i)
            pHost = page.host
            if host['addr'] == pHost:
                self.hosts[i]['name'] = config['player_name']
                self.SetPageText(i, config['player_name'])

    def UpdateCurrentPlayerUI(self, config):
        self.hosts[self.activePageNr]['name'] = config['player_name']
        self.GetPage(self.activePageNr).UpdateConfigUI(config, True)

    def UpdatePageName(self, oldName, newName):
        for i in range(self.GetPageCount()):
            page = self.GetPage(i)
            label = page.GetLabel()
            found = label == oldName
            if found:
                self.SetPageText(i, newName)

    def HostFound(self, host, playerName, freeSpace=None):
        if freeSpace == None:
            freeSpace = (0,0)
        global playerCount
        if not self.HostInList(host[0], playerName):
            self.hosts.append({"addr": host[0], "name": playerName, "free": freeSpace})
            playerCount += 1

    def SortHostList(self):
        sortedList = sorted(self.hosts, key=itemgetter('name'))
        self.hosts = sortedList

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
        if self.hostSearch:
            self.hostSearch = False
            if playerCount == 0:
                self.prgDialog.Update(100)
                if HOST_SYS == HOST_WIN:
                    self.prgDialog.Destroy()
                    if platform.release() == "XP":
                        dlgWin = wx.MessageDialog(self,wordwrap(tr("no_players_found"), 300, wx.ClientDC(self)), tr("no_player"), style=wx.OK)
                        result = dlgWin.ShowModal()
                        self.parent.Close()
                dlg = wx.SingleChoiceDialog(self,wordwrap(tr("no_players_found"), 300, wx.ClientDC(self)), tr("no_player"), ["Enter IP Address", tr("rescan"), tr("exit")])
                result = dlg.ShowModal()
                selection = dlg.GetSelection()
                if result == wx.ID_OK:
                    if selection == 0: # ENTER IP
                        ipDlg = wx.TextEntryDialog(self, "Enter the IP of your RaspMedia Player or Exit application with cancel.", "Enter IP Address");
                        if ipDlg.ShowModal() == wx.ID_OK:
                            ipAddress = ipDlg.GetValue()
                            self.HostFound([ipAddress, "RaspMedia"], "RaspMedia")
                            self.LoadControlWindowForCurrentHostList()
                        else:
                            self.parent.Close()
                    elif selection == 1: # RESCAN
                        self.SearchHosts()
                    elif selection == 2: # EXIT
                        self.parent.Close()
                elif result == wx.ID_CANCEL:
                    self.parent.Close()
            else:
                self.LoadControlWindowForCurrentHostList()

    def LoadControlWindowForCurrentHostList(self):
        ind = 0
        # sort hosts by hostname
        self.SortHostList()
        for host in self.hosts:
            curPage = rmc.RaspMediaCtrlPanel(self,-1,host['name'],ind,host['addr'],host['free'],HOST_SYS)
            self.pages.append(curPage)
            self.AddPage(curPage, host['name'])
            ind += 1


        allPlayers = rmap.RaspMediaAllPlayersPanel(self,-1,"All Players",ind,self.hosts,HOST_SYS)
        self.pages.append(allPlayers)
        self.AddPage(allPlayers, "All Players")

        self.LoadPageData(0)
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
