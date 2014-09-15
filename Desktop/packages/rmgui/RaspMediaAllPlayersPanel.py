import packages.rmnetwork as network
import packages.rmutil as rmutil
from packages.rmgui import *
import GroupEditDialog as groupDlg
import PlayerInfoDialog as playerDlg
import ActionEditFrame as actionFrame
from packages.rmnetwork.constants import *
from packages.lang.Localizer import *
import os, sys, platform, ast, time, threading, shutil, copy

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
# RASP MEDIA ALL PLAYERS PANEL #################################################
################################################################################
class RaspMediaAllPlayersPanel(wx.Panel):
    def __init__(self,parent,id,title,index,hosts,host_sys):
        #wx.Panel.__init__(self,parent,id,title)
        wx.Panel.__init__(self,parent,-1)
        global HOST_SYS, BASE_PATH
        HOST_SYS = host_sys
        BASE_PATH = parent.parent.base_path
        self.parent = parent
        self.index = index
        self.hosts = sorted(hosts)
        self.memberHosts = []
        self.availableHosts = list(self.hosts)
        self.nameLabels = {}
        self.groupConfigs = []
        self.groups = {}

        self.groupDeletion = False
        self.groupLoading = True

        self.mainSizer = wx.GridBagSizer()
        self.leftSizer = wx.GridBagSizer()
        self.rightSizer = wx.GridBagSizer()
        self.groupSizer = wx.GridBagSizer()
        self.notebook_event = None
        self.prgDialog = None
        self.Initialize()


    def SetHost(self, hostAddress):
        self.host = hostAddress

    def LoadData(self):
        for host in self.parent.hosts:
            for curHost in self.hosts:
                if host['addr'] == curHost['addr']:
                    curHost['name'] = host['name']
                    self.nameLabels[curHost['addr']].SetLabel(curHost['name'])

        self.LoadGroupConfig()

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
        # setup UI in sizers
        self.SetupPlayerSection()
        self.SetupControlSection()
        self.SetupGroupSection()

        # add sizers to main sizer
        self.mainSizer.Add(self.scroll ,(0,0), span=(2,1), flag=wx.ALIGN_CENTER_HORIZONTAL | wx.LEFT | wx.RIGHT, border=15)
        self.mainSizer.Add(self.rightSizer, (0,2), flag = wx.ALL, border=10)
        self.mainSizer.Add(self.groupScroll, (1,2), flag = wx.TOP | wx.RIGHT | wx.LEFT, border=10)

        self.SetSizerAndFit(self.mainSizer)

        #line = wx.StaticLine(self,-1,size=(self.mainSizer.GetSize()[0],2))
        #self.mainSizer.Add(line, (1,0), span=(1,4))

        #line = wx.StaticLine(self,-1,size=(2,self.mainSizer.GetCellSize(0,0)[1]),style=wx.LI_VERTICAL)
        #self.mainSizer.Add(line,(0,1), flag = wx.LEFT, border = 10)

        #self.Fit()
        line = wx.StaticLine(self,-1,size=(2,565),style=wx.LI_VERTICAL)
        self.mainSizer.Add(line,(0,1), span=(2,1), flag=wx.LEFT | wx.RIGHT, border=5)

        self.Show(True)

    def SetupPlayerSection(self):
        # scrolled panel to show player status list
        self.scroll = wx.lib.scrolledpanel.ScrolledPanel(self, -1, size=(280,565))
        self.scroll.SetAutoLayout(1)
        self.scroll.SetupScrolling(scroll_x=False, scroll_y=True)
        self.scroll.SetSizer(self.leftSizer)

        index = 0
        # name, ip and a rename button for each host
        for host in sorted(self.hosts):

            playerBox = wx.StaticBox(self.scroll,-1,label=host['name'])
            boxSizer = wx.StaticBoxSizer(playerBox, wx.VERTICAL)

            self.nameLabels[host['addr']] = playerBox

            ip = wx.StaticText(self.scroll,-1,label=host['addr'],size=(110,25))
            setName = wx.Button(self.scroll,-1,label="Player Name",size=(110,25))
            identify = wx.Button(self.scroll,-1,label=tr("identify"),size=(110,25))

            ipLabel = wx.StaticText(self.scroll,-1,label="Player IP:",size=(110,25))

            ipSizer = wx.BoxSizer()
            ipSizer.Add(ipLabel,flag=wx.ALL, border = 5)
            ipSizer.Add(ip, flag=wx.ALIGN_RIGHT | wx.ALL, border = 5)

            btnSizer = wx.BoxSizer()
            btnSizer.Add(identify, flag=wx.ALL, border = 5)
            btnSizer.Add(setName, flag=wx.ALIGN_RIGHT|wx.ALL, border = 5)

            # add UI elements to box
            boxSizer.Add(ipSizer)
            boxSizer.Add(btnSizer)

            # add status UI for current host
            self.leftSizer.Add(boxSizer, (index,0), flag=wx.ALL, border=5)
            index += 1


            self.Bind(wx.EVT_BUTTON, lambda event, host=host: self.UpdatePlayerName(event,host), setName)
            self.Bind(wx.EVT_BUTTON, lambda event, host=host: self.IdentifyPlayer(event,host), identify)


    def SetupControlSection(self):
        ctrlBox = wx.StaticBox(self,-1,label="Master Control")
        boxSizer = wx.StaticBoxSizer(ctrlBox, wx.VERTICAL)

        # setup controls
        startAll = wx.Button(self,-1,label=tr("restart_all"), size=(200,25))
        stopAll = wx.Button(self,-1,label=tr("stop_all"), size=(200,25))
        identAll = wx.Button(self,-1,label=tr("identify_all"), size=(200,25))
        rebootAll = wx.Button(self,-1,label=tr("reboot_all"), size=(200,25))
        update = wx.Button(self,-1,label="Update All", size=(200,25))

        # bind events
        self.Bind(wx.EVT_BUTTON, self.RestartAllPlayers, startAll)
        self.Bind(wx.EVT_BUTTON, self.StopAllPlayers, stopAll)
        self.Bind(wx.EVT_BUTTON, self.IdentifyAllPlayers, identAll)
        self.Bind(wx.EVT_BUTTON, self.RebootAllPlayers, rebootAll)
        self.Bind(wx.EVT_BUTTON, self.UpdateAllPlayers, update)

        line = wx.StaticLine(self,-1,size=(260,2))

        boxSizer.Add(startAll, flag=wx.LEFT, border=5)
        boxSizer.Add(stopAll, flag=wx.ALL, border=5)
        boxSizer.Add(identAll, flag=wx.LEFT, border=5)
        boxSizer.Add(rebootAll, flag=wx.ALL, border=5)
        boxSizer.Add(update, flag=wx.LEFT, border=5)

        self.rightSizer.Add(boxSizer,(0,0))
        self.rightSizer.Add(line, (1,0), flag=wx.ALL, border=5)

    def UpdateAllPlayers(self, event=None):
        dlg = wx.MessageDialog(self, "Updating all players, RaspMedia Control needs to be closed. Restart application when players have updated and rebooted.", "Update all players", style = wx.YES_NO)
        if dlg.ShowModal() == wx.ID_YES:
            msgData = network.messages.getMessage(PLAYER_UPDATE)
            network.udpconnector.sendMessage(msgData)
            if HOST_SYS == HOST_WIN:
                dlg.Destroy()
            self.parent.parent.Close()


    def SetupGroupSection(self):
        # scrolled panel to show player groups
        self.groupScroll = wx.lib.scrolledpanel.ScrolledPanel(self, -1, size=(290,345))
        self.groupScroll.SetAutoLayout(1)
        self.groupScroll.SetupScrolling(scroll_x=False, scroll_y=True)
        self.groupSizer.SetMinSize((300,250))
        self.groupScroll.SetSizer(self.groupSizer)


    def LoadGroupUI(self):
        # clear sizer when updating group configurations in UI
        self.groupSizer.Clear(True)

        # add new group button
        gNew = wx.Button(self.groupScroll,-1,label=tr("new_group"))
        self.Bind(wx.EVT_BUTTON, self.NewGroupClicked, gNew)

        #self.groupSizer.Add(gLabel, (0,0))
        self.groupSizer.Add(gNew, (0,0), flag = wx.LEFT, border = 5)

        # parse group configurations and create UI elements
        self.ParseGroups()

        index = 1
        for group in self.groups:
            name = self.groups[group]["name"]

            box = wx.StaticBox(self.groupScroll,-1,name)
            groupSizer = wx.StaticBoxSizer(box, wx.VERTICAL)

            memberList = wx.ListCtrl(self.groupScroll,-1,size=(255,80), style=wx.LC_REPORT|wx.SUNKEN_BORDER)
            memberList.Show(True)
            memberList.InsertColumn(0,tr("player_name"), width = 145)
            memberList.InsertColumn(1,"Master", width = 50, format = wx.LIST_FORMAT_CENTER)
            memberList.InsertColumn(2,"Member", width = 50, format = wx.LIST_FORMAT_CENTER)

            members = self.groups[group]['members']
            for member in members:
                idx = memberList.InsertStringItem(memberList.GetItemCount(), member['player_name'])
                if member['master']:
                    memberList.SetStringItem(idx, 1, "*")
                else:
                    memberList.SetStringItem(idx, 2, "*")

            editGroup = wx.Button(self.groupScroll,-1,label=tr("edit"),size=(85,25))
            editAct = wx.Button(self.groupScroll,-1,label=tr("actions"),size=(85,25))
            delGroup = wx.Button(self.groupScroll,-1,label=tr("delete"),size=(85,25))

            self.Bind(wx.EVT_BUTTON, lambda event, group=self.groups[group]: self.EditGroup(event,group), editGroup)
            self.Bind(wx.EVT_BUTTON, lambda event, group=self.groups[group]: self.EditActions(event,group), editAct)
            self.Bind(wx.EVT_BUTTON, lambda event, group=self.groups[group]: self.DeleteGroup(event,group), delGroup)
            self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, lambda event, group=self.groups[group], list=memberList: self.MemberDetails(event,group,list), memberList)

            # add UI elements
            groupSizer.Add(memberList)
            btnSizer = wx.GridBagSizer()
            btnSizer.Add(editGroup, (0,0))
            btnSizer.Add(editAct, (0,1))
            btnSizer.Add(delGroup, (0,2))
            groupSizer.Add(btnSizer)

            index +=1
            self.groupSizer.Add(groupSizer, (index, 0), span=(1,2))


        self.groupSizer.Layout()
        self.groupScroll.SetupScrolling(scroll_x=False, scroll_y=True)

    def EditGroup(self, event, group):
        editHosts = list(self.availableHosts)
        for host in group['members']:
            editHosts.append({'addr': host['ip'], 'name': host['player_name']})

        dlg = groupDlg.GroupEditDialog(self,-1,tr("edit"),editHosts,group=group)
        if dlg.ShowModal() == wx.ID_OK:
            dlg = wx.ProgressDialog(tr("saving"), tr("saving_group"), parent = self, style = wx.PD_AUTO_HIDE)
            dlg.Pulse()
            time.sleep(len(self.hosts))
            dlg.Update(100)
            if HOST_SYS == HOST_WIN:
                dlg.Destroy()
            self.LoadGroupConfig()

    def EditActions(self, event, group):
        frame = actionFrame.ActionEditFrame(self,-1,tr("actions"),self.hosts,group=group)
        frame.Show(True)
        frame.MakeModal(True)

    def DeleteGroup(self, event, group):
        qDlg = wx.MessageDialog(self,tr("delete_group") % group['name'], tr("delete"), style = wx.YES_NO)
        if qDlg.ShowModal() == wx.ID_YES:
            self.groupDeletion = True
            msgData = network.messages.getMessage(GROUP_DELETE, ["-s", group['name']])
            Publisher.subscribe(self.UdpListenerStopped, 'listener_stop')
            dlgStyle = wx.PD_AUTO_HIDE
            self.prgDialog = wx.ProgressDialog(tr("deleting_group") % group['name'], tr("delete"), parent = self, style = dlgStyle)
            self.prgDialog.Pulse()
            network.udpconnector.sendMessage(msgData)

    def MemberDetails(self, event, group, list):
        item = event.GetItem()
        index = list.GetFirstSelected()
        dlg = playerDlg.PlayerInfoDialog(self,-1,"Player Info",group['members'][index])
        dlg.ShowModal()

    def NewGroupClicked(self, event=None):
        dlg = groupDlg.GroupEditDialog(self,-1,tr("new_group"),self.availableHosts)
        if dlg.ShowModal() == wx.ID_OK:
            dlg = wx.ProgressDialog(tr("saving"), tr("saving_group"), parent = self, style = wx.PD_AUTO_HIDE)
            dlg.Pulse()
            time.sleep(len(self.hosts))
            dlg.Update(100)
            if HOST_SYS == HOST_WIN:
                dlg.Destroy()
            self.LoadGroupConfig()


    def LoadGroupConfig(self, event=None):
        # reset previously loaded group config data
        self.groups = {}
        self.groupConfigs = []
        self.availableHosts = list(self.hosts)
        self.memberHosts = []

        self.groupLoading = True
        Publisher.subscribe(self.GroupConfigReceived, 'group_config')
        Publisher.subscribe(self.UdpListenerStopped, 'listener_stop')
        msgData = network.messages.getMessage(GROUP_CONFIG_REQUEST)
        dlgStyle = wx.PD_AUTO_HIDE
        self.prgDialog = wx.ProgressDialog(tr("loading"), tr("loading_group_config"), parent = self, style = dlgStyle)
        self.prgDialog.Pulse()
        network.udpconnector.sendMessage(msgData)

    def UpdatePlayerName(self, event, host):
        dlg = wx.TextEntryDialog(self, tr("new_name")+":", tr("player_name"), host['name'])
        if dlg.ShowModal() == wx.ID_OK:
            newName = dlg.GetValue()
            oldName = host['name']
            host['name'] = newName
            # set new name in player box and page tab
            self.nameLabels[host['addr']].SetLabel(newName)
            self.parent.UpdatePageName(oldName,newName)
            # send new name to player
            msgData = network.messages.getConfigUpdateMessage("player_name", str(newName))
            network.udpconnector.sendMessage(msgData, host['addr'])
            time.sleep(0.2)
            self.LoadGroupConfig()
        dlg.Destroy()

    def RestartAllPlayers(self, event=None):
        msgData = network.messages.getMessage(PLAYER_RESTART)
        network.udpconnector.sendMessage(msgData)

    def StopAllPlayers(self, event=None):
        msgData = network.messages.getMessage(PLAYER_STOP)
        network.udpconnector.sendMessage(msgData)

    def RebootAllPlayers(self, event=None):
        dlg = wx.MessageDialog(self, tr("reboot_all_info"), tr("reboot_all"), style = wx.YES_NO)
        if dlg.ShowModal() == wx.ID_YES:
            msgData = network.messages.getMessage(PLAYER_REBOOT)
            network.udpconnector.sendMessage(msgData)
            if HOST_SYS == HOST_WIN:
                dlg.Destroy()
            self.parent.parent.Close()


    def IdentifyPlayer(self, event, host):
        msgData = network.messages.getMessage(PLAYER_IDENTIFY)
        network.udpconnector.sendMessage(msgData, host['addr'])
        msg = tr("dlg_msg_identify")
        dlg = wx.MessageDialog(self, msg, tr("dlg_title_identify"), wx.OK | wx.ICON_EXCLAMATION)
        if dlg.ShowModal() == wx.ID_OK:
            msgData2 = network.messages.getMessage(PLAYER_IDENTIFY_DONE)
            network.udpconnector.sendMessage(msgData2, host['addr'])
        dlg.Destroy()

    def IdentifyAllPlayers(self, event=None):
        msgData = network.messages.getMessage(PLAYER_IDENTIFY)
        network.udpconnector.sendMessage(msgData)
        msg = tr("dlg_msg_identify")
        dlg = wx.MessageDialog(self, msg, tr("dlg_title_identify"), wx.OK | wx.ICON_EXCLAMATION)
        if dlg.ShowModal() == wx.ID_OK:
            msgData2 = network.messages.getMessage(PLAYER_IDENTIFY_DONE)
            network.udpconnector.sendMessage(msgData2)
        dlg.Destroy()

    def GroupConfigReceived(self, group_config, playerIP, isDict=False):
        global HOST_SYS
        if isDict:
            configDict = group_config
        else:
            configDict = ast.literal_eval(group_config)

        configDict["player_ip"] = playerIP

        # save group configuration, parsing is done when all configs are loaded
        self.groupConfigs.append(configDict)

    def UdpListenerStopped(self):
        global HOST_SYS
        if self.prgDialog:
            self.prgDialog.Update(100)
            if HOST_SYS == HOST_WIN:
                self.prgDialog.Destroy()
        if self.groupLoading:
            self.LoadGroupUI()
            self.groupLoading = False
        elif self.groupDeletion:
            self.LoadGroupConfig()
            self.groupDeletion = False

    def ParseGroups(self):
        # parse configurations
        for conf in self.groupConfigs:
            # read current config
            name = conf['group']
            if not name == None:
                actions = []
                if "actions" in conf:
                    actions = conf['actions']
                ip = conf['player_ip']
                master = conf['group_master']
                member = {}
                member['ip'] = ip
                found = False
                for host in self.hosts:
                    if ip == host['addr']:
                        member['player_name'] = host['name']
                        found = True
                        self.memberHosts.append(host)
                if found:
                    member['master'] = master
                    members = []
                    group = {}

                    if not name in self.groups:
                        group['name'] = name
                        group['members'] = members
                        group['members'].append(member)
                        group['actions'] = actions
                        self.groups[name] = group
                    else:
                        self.groups[name]['members'].append(member)
                        if len(actions) > 0:
                            self.groups[name]['actions'] = actions
        for group in self.groups:
            self.groups[group]['members'] = sorted(self.groups[group]['members'])

        self.UpdateAvailableHosts()


    def UpdateAvailableHosts(self):
        for host in self.memberHosts:
            if host in self.availableHosts:
                ind = self.availableHosts.index(host)
                del self.availableHosts[ind]

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
        #Publisher.subscribe(self.UdpListenerStopped, 'listener_stop')
        self.prgDialog.Pulse()

        msgData = network.messages.getMessage(PLAYER_REBOOT)
        network.udpconnector.sendMessage(msgData, self.host, UDP_REBOOT_TIMEOUT)

    def RebootComplete(self):
        # print "REBOOT COMPLETE CALLBACK"
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
