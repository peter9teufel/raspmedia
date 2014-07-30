import wx
import sys
from packages.rmnetwork import netutil
import packages.rmnetwork as network
from packages.lang.Localizer import *

################################################################################
# DIALOG FOR WIFI CONFIG #######################################################
################################################################################
class WifiDialog(wx.Dialog):
    def __init__(self,parent,id,title,host):
        wx.Dialog.__init__(self,parent,id,title)
        self.parent = parent
        self.host = host
        self.mainSizer = wx.GridBagSizer()
        self.manualSSID = False
        self.SSID = ''
        self.__InitUI()
        self.SetSizerAndFit(self.mainSizer)

    def __InitUI(self):
        labelSSID = wx.StaticText(self, -1, label=tr("wifi_ssid") + ":")
        labelPwd = wx.StaticText(self, -1, label=tr("wifi_key") + ":")
        self.pwdTextCtrl = wx.TextCtrl(self, -1, style=wx.TE_PASSWORD)

        wifis = netutil.wifi_ssids()
        if len(wifis) > 0:
            # offer available wifi networks in combo box
            self.combo = wx.ComboBox(self, -1, choices=wifis)
            self.Bind(wx.EVT_COMBOBOX, self.__SSIDSelected, self.combo)
        else:
            # Wifi maybe hidden or no wireless adapter active --> user can input SSID
            self.manualSSID = True
            self.ssidTxtCtrl = wx.TextCtrl(self, -1)

        okBtn = wx.Button(self, wx.ID_OK, tr("ok"))
        cancelBtn = wx.Button(self, wx.ID_CANCEL, tr("cancel"))

        # bind buttons
        self.Bind(wx.EVT_BUTTON, self.okClicked, okBtn)
        self.Bind(wx.EVT_BUTTON, self.cancelClicked, cancelBtn)

        # add UI elements to sizer
        self.mainSizer.Add(labelSSID, (0,0), flag = wx.ALL, border = 5)
        if self.manualSSID:
            self.mainSizer.Add(self.ssidTxtCtrl, (0,1), flag = wx.ALL, border = 5)
        else:
            self.mainSizer.Add(self.combo, (0,1), flag = wx.ALL, border = 5)
        self.mainSizer.Add(labelPwd, (1,0), flag = wx.ALL, border = 5)
        self.mainSizer.Add(self.pwdTextCtrl, (1,1), flag = wx.ALL, border = 5)
        self.mainSizer.Add(cancelBtn, (2,0), flag = wx.ALL, border = 5)
        self.mainSizer.Add(okBtn, (2,1), flag = wx.ALL, border = 5)

    def okClicked(self, event):
        # send config to player
        msgData = network.messages.getWifiConfigMessage(self.SSID, self.pwdTextCtrl.GetValue())
        network.udpconnector.sendMessage(msgData, self.host)
        self.EndModal(wx.ID_OK)
        self.Destroy()

    def cancelClicked(self, event):
        self.EndModal(wx.ID_CANCEL)
        self.Destroy()

    def __SSIDSelected(self, event=None):
        self.SSID = self.combo.GetValue()
