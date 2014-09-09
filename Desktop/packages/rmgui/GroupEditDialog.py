import wx
import sys, platform, time
from wx.lib.wordwrap import wordwrap
from packages.rmnetwork import netutil
import packages.rmnetwork as network
from packages.rmnetwork.constants import *
from packages.lang.Localizer import *

################################################################################
# DIALOG FOR GROUP CREATION AND EDITING ########################################
################################################################################
class GroupEditDialog(wx.Dialog):
    def __init__(self,parent,id,title,hosts,actions=[],group=None):
        wx.Dialog.__init__(self,parent,id,title)
        self.parent = parent
        self.hosts = hosts
        self.actions = actions
        self.members = []
        self.master = -1
        self.mainSizer = wx.GridBagSizer()
        self.__InitUI()
        if group:
            self.UpdateUI(group)
        self.SetSizerAndFit(self.mainSizer)
        self.Center()

    def __InitUI(self):
        # labels and textctrl for group name
        nameLabel = wx.StaticText(self,-1,label=tr("name")+":")
        self.membersLabel = wx.StaticText(self,-1,label=tr("members")+":")
        self.masterLabel = wx.StaticText(self,-1,label=tr("master"))
        self.nameCtrl = wx.TextCtrl(self, -1, size = (200,25))

        # buttons
        editMembers = wx.Button(self,-1,label="Edit Members", size=(200,25))
        self.okBtn = wx.Button(self, wx.ID_OK, label="OK", size=(140,25))
        cancelBtn = wx.Button(self, wx.ID_CANCEL, label=tr("cancel"), size=(140,25))

        # combo box for available wifis (scanned later)
        masters = [""]
        self.combo = wx.ComboBox(self, -1, value=masters[0], choices=masters, size = (200,25))
        self.Bind(wx.EVT_COMBOBOX, self.__MasterSelected, self.combo)

        # bind buttons
        self.Bind(wx.EVT_BUTTON, self.SelectMembers, editMembers)
        self.Bind(wx.EVT_TEXT, self.__ValidateInput, self.nameCtrl)
        self.Bind(wx.EVT_BUTTON, self.okClicked, self.okBtn)
        self.Bind(wx.EVT_BUTTON, self.cancelClicked, cancelBtn)

        # add ui elements to main sizer
        self.mainSizer.Add(nameLabel, (0,0), flag = wx.LEFT | wx.TOP, border = 10)
        self.mainSizer.Add(self.nameCtrl, (0,1), flag = wx.RIGHT | wx.TOP | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        self.mainSizer.Add(self.membersLabel, (1,0), flag = wx.LEFT | wx.TOP, border = 10)
        self.mainSizer.Add(editMembers, (1,1), flag = wx.RIGHT | wx.ALIGN_RIGHT | wx.TOP | wx.ALIGN_CENTER_VERTICAL, border = 10)
        self.mainSizer.Add(self.masterLabel, (2,0), flag = wx.LEFT, border = 10)
        self.mainSizer.Add(self.combo, (2,1), flag = wx.RIGHT | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        self.mainSizer.Add(cancelBtn, (5,0), flag = wx.LEFT | wx.BOTTOM | wx.ALIGN_RIGHT, border = 10)
        self.mainSizer.Add(self.okBtn, (5,1), flag = wx.RIGHT | wx.ALIGN_RIGHT | wx.BOTTOM, border = 10)

        self.__ValidateInput()

    def UpdateUI(self, group):
        self.nameCtrl.SetValue(group['name'])
        members = group['members']
        for member in members:
            ip = member['ip']
            name = member['player_name']
            master = member['master']
            index = get_index(self.hosts, 'addr', ip)
            self.members.append(index)
            if master:
                self.master = index
            self.UpdateAvailableMasters()


    def SelectMembers(self, event):
        hostNames = []
        for host in self.hosts:
            hostNames.append(host['name'])
        dlg = wx.MultiChoiceDialog(self,wordwrap(tr("msg_select_members"), 300, wx.ClientDC(self)), tr("members"), hostNames)
        dlg.SetSelections(self.members)
        result = dlg.ShowModal()
        selection = dlg.GetSelections()
        # print "RESULT: ", result
        if result == wx.ID_OK:
            # print "OK clicked, checking selected index... ", selection
            self.members = selection
            self.membersLabel.SetLabel("%s: %d" % (tr("members"),len(self.members)))
            if not self.master in self.members:
                self.master = -1
            self.UpdateAvailableMasters()


    def UpdateAvailableMasters(self):
        self.masterHosts = []
        names = []
        for index in self.members:
            self.masterHosts.append({"name": self.hosts[index]['name'], "index": index})
            names.append(self.hosts[index]['name'])

        self.combo.SetItems(names)

        if not self.master == -1 and self.master in self.members:
            index = -1
            for i in range(len(names)):
                if names[i] == self.hosts[self.master]['name']:
                    index = i
            # set selected master in combo box
            self.combo.SetSelection(i)
        else:
            self.combo.SetSelection(-1)
            self.master == -1

        self.__ValidateInput()


    def __MasterSelected(self, event=None):
        selection = self.combo.GetSelection()
        if not selection == -1:
            self.master = self.masterHosts[selection]["index"]
            self.__ValidateInput()


    def okClicked(self, event):
        name = self.nameCtrl.GetValue()
        masterIP = self.hosts[self.master]['addr']
        actions = self.actions
        master = "0"

        # SEND GROUP CONFIG TO MASTER AND MEMBERS
        for member in self.members:
            if member == self.master:
                # member index == master index --> set master flag
                master = "1"
            else:
                # member --> master flag is false
                master = "0"
            msgData = network.messages.getMessage(GROUP_CONFIG, ['-s',name,'-i',master])
            network.udpconnector.sendMessage(msgData, self.hosts[member]['addr'])

        self.EndModal(wx.ID_OK)
        self.Destroy()

    def cancelClicked(self, event):
        self.EndModal(wx.ID_CANCEL)
        self.Destroy()

    def __ValidateInput(self, event=None):
        if not self.nameCtrl.GetValue() == "" and len(self.members) > 0 and not self.master == -1:
            self.okBtn.Enable()
        else:
            self.okBtn.Disable()

def get_index(seq, attr, value):
    return next(index for (index, d) in enumerate(seq) if d[attr] == value)
