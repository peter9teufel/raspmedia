import wx
import sys, platform
from wx.lib.wordwrap import wordwrap
from packages.rmnetwork import netutil
import packages.rmnetwork as network
from packages.rmnetwork.constants import *
from packages.lang.Localizer import *

################################################################################
# DIALOG FOR GROUP CREATION AND EDITING ########################################
################################################################################
class PlayerInfoDialog(wx.Dialog):
    def __init__(self,parent,id,title,player_info):
        wx.Dialog.__init__(self,parent,id,title)
        self.parent = parent
        self.player_info = player_info
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.__InitUI()

        self.SetSizerAndFit(self.mainSizer)
        self.Center()

    def __InitUI(self):
        # labels and textctrl for group name
        nameLabel = wx.StaticText(self,-1,label="Name: " + self.player_info['player_name'])
        ipLabel = wx.StaticText(self,-1,label="IP: " + self.player_info['ip'])

        # buttons
        okBtn = wx.Button(self, wx.ID_OK, label="OK", size=(140,25))

        # bind buttons
        self.Bind(wx.EVT_BUTTON, self.okClicked, okBtn)

        # add ui elements to main sizer
        self.mainSizer.Add(nameLabel, flag = wx.ALL, border = 10)
        self.mainSizer.Add(ipLabel, flag = wx.LEFT, border = 10)
        self.mainSizer.Add(okBtn, flag = wx.ALL, border = 10)


    def okClicked(self, event):
        self.EndModal(wx.ID_OK)
        self.Destroy()
