import wx
import sys, platform
from packages.rmnetwork import netutil
import packages.rmnetwork as network
from packages.rmnetwork.constants import *
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
        self.SSID = ''
        self.__InitUI()
        self.SetSizerAndFit(self.mainSizer)
        self.Center()
        self.ScanForAvailableWifis()

    def __InitUI(self):
        labelSSID = wx.StaticText(self, -1, label=tr("wifi_ssid") + ":")
        labelPwd = wx.StaticText(self, -1, label=tr("wifi_key") + ":")
        self.pwdTextCtrl = wx.TextCtrl(self, -1, style=wx.TE_PASSWORD, size = (200,25))

        wifis = []
        wifis.append("")

        # combo box for available wifis (scanned later)
        self.combo = wx.ComboBox(self, -1, value=wifis[0], choices=wifis, size = (203,25))
        self.Bind(wx.EVT_COMBOBOX, self.__SSIDSelected, self.combo)
        self.combo.Bind(wx.EVT_TEXT, self.__SSIDSelected)

        # radio box for selecting auth type for manual SSID
        self.authRBox = wx.RadioBox(self, -1, label=tr("auth_type"), choices=["WPA","WEP","NONE"])

        self.okBtn = wx.Button(self, wx.ID_OK, tr("ok"))
        self.okBtn.Disable()
        cancelBtn = wx.Button(self, wx.ID_CANCEL, tr("cancel"))

        # bind ui elements
        self.Bind(wx.EVT_BUTTON, self.okClicked, self.okBtn)
        self.Bind(wx.EVT_BUTTON, self.cancelClicked, cancelBtn)
        self.pwdTextCtrl.Bind(wx.EVT_TEXT, self.__ValidateInput)
        self.authRBox.Bind(wx.EVT_RADIOBOX, self.__ValidateInput)

        # add UI elements to sizer
        self.mainSizer.Add(labelSSID, (0,0), flag = wx.LEFT | wx.TOP | wx.ALIGN_LEFT, border = 25)
        self.mainSizer.Add(self.combo, (0,1), flag = wx.TOP | wx.RIGHT | wx.ALIGN_LEFT, border = 25)
        self.mainSizer.Add(labelPwd, (1,0), flag = wx.LEFT | wx.ALIGN_LEFT, border = 25)
        self.mainSizer.Add(self.pwdTextCtrl, (1,1), flag = wx.RIGHT | wx.ALIGN_LEFT, border = 25)
        self.mainSizer.Add(self.authRBox, (3,0), span=(1,2), flag = wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT, border = 25)
        self.mainSizer.Add(cancelBtn, (4,0), flag = wx.ALL | wx.ALIGN_LEFT, border = 15)
        self.mainSizer.Add(self.okBtn, (4,1), flag = wx.ALL | wx.ALIGN_RIGHT, border = 15)

    def ScanForAvailableWifis(self):
        dlg = wx.ProgressDialog(tr("scanning"), tr("scanning_wifis"), style = wx.PD_AUTO_HIDE)
        dlg.Pulse()
        self.wifis = netutil.wifi_ssids()
        wifis = []
        for wifi in self.wifis:
            wifis.append(wifi["SSID"])
        self.combo.AppendItems(wifis)
        dlg.Update(100)
        if platform.system() == "Windows":
            dlg.Destroy()

    def okClicked(self, event):
        # send config to player
        selWifi = None
        for wifi in self.wifis:
            if wifi["SSID"] == self.SSID:
                selWifi = wifi
        if selWifi == None:
            authType = None
            sel = self.authRBox.GetSelection()
            if sel == 0:
                authType = WIFI_AUTH_WPA
            elif sel == 1:
                authType = WIFI_AUTH_WEP
            elif sel == 2:
                authType = WIFI_AUTH_NONE
            selWifi = {"SSID": self.SSID, "AUTHTYPE": authType}
        msgData = network.messages.getWifiConfigMessage(selWifi, self.pwdTextCtrl.GetValue())
        network.udpconnector.sendMessage(msgData, self.host)
        self.EndModal(wx.ID_OK)
        self.Destroy()

    def cancelClicked(self, event):
        self.EndModal(wx.ID_CANCEL)
        self.Destroy()

    def __ValidateInput(self, event=None):
        ssidSet = len(self.SSID) > 0
        keySet = len(self.pwdTextCtrl.GetValue()) > 0

        authType = None
        for wifi in self.wifis:
            if wifi["SSID"] == self.SSID:
                authType = wifi["AUTHTYPE"]
        if authType == None:
            self.authRBox.Enable()
        else:
            self.authRBox.Disable()
            if authType == WIFI_AUTH_WPA:
                self.authRBox.SetSelection(0)
            elif authType == WIFI_AUTH_WEP:
                self.authRBox.SetSelection(1)
            elif authType == WIFI_AUTH_NONE:
                self.authRBox.SetSelection(2)

        if (ssidSet and keySet) or (ssidSet and self.authRBox.GetSelection() == 2):
            self.okBtn.Enable()
        else:
            self.okBtn.Disable()

    def __SSIDSelected(self, event=None):
        self.SSID = self.combo.GetValue()
        self.__ValidateInput()
