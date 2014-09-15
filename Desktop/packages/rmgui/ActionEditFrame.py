import wx
import sys, platform, time, ast
from packages.rmnetwork import netutil
import packages.rmnetwork as network
from packages.rmnetwork.constants import *
from packages.lang.Localizer import *

from wx.lib.wordwrap import wordwrap
import wx.lib.scrolledpanel as scrolled
if platform.system() == "Linux":
    from wx.lib.pubsub import setupkwargs
    from wx.lib.pubsub import pub as Publisher
else:
    from wx.lib.pubsub import pub as Publisher

# mapping from combo choices to constant codes
CMD = ['play', 'stop', 'restart', 'reboot', 'update']
CMD_CODE = [PLAYER_START, PLAYER_STOP, PLAYER_RESTART, PLAYER_REBOOT, PLAYER_UPDATE]
TYPE = ['startup', 'new_player_found', 'per_sec', 'per_min', 'per_hour']
TYPE_CODE = [ACTION_EVENT_STARTUP, ACTION_EVENT_NEW_PLAYER, PERIODIC_SEC, PERIODIC_MIN, PERIODIC_HOUR]
TYPE_ONETIME = [ACTION_EVENT_STARTUP, ACTION_EVENT_NEW_PLAYER]

################################################################################
# FRAME FOR ACTION EDITING #####################################################
################################################################################
class ActionEditFrame(wx.Frame):
    def __init__(self,parent,id,title,hosts,group):
        wx.Frame.__init__(self,parent,id,title)
        self.parent = parent
        self.hosts = hosts
        self.Bind(wx.EVT_CLOSE, self.Close)
        self.group = group
        self.currentAction = None
        self.actionSaved = True
        self.actions = []
        self.masterHost = ""
        if "actions" in group:
            self.actions = group['actions']
        for member in self.group['members']:
            if member['master']:
                self.masterHost = member['ip']
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.__InitUI()
        self.SetSizerAndFit(self.mainSizer)
        self.Center()

    def __InitUI(self):
        self.headSizer = wx.BoxSizer(wx.VERTICAL)
        self.contentSizer = wx.BoxSizer(wx.VERTICAL)
        self.actScroll = scrolled.ScrolledPanel(self, -1, (437,200))
        self.actScroll.SetAutoLayout(1)
        self.actScroll.SetupScrolling(scroll_x=True, scroll_y=True)
        self.actScroll.SetMinSize((437,200))
        self.contentSizer.SetMinSize((415,195))
        self.actScroll.SetSizer(self.contentSizer)


        self.SetupHeadSection()

        self.LoadActionUI()

        # close button
        self.okBtn = wx.Button(self,-1,label="OK")
        self.Bind(wx.EVT_BUTTON, self.Close, self.okBtn)

        # divider line between sections
        line = wx.StaticLine(self, -1, size = (437,2))
        secLine = wx.StaticLine(self, -1, size = (437,2))
        lineBottom = wx.StaticLine(self, -1, size = (437,2))

        # add content sizers and section dividers to main sizer
        self.mainSizer.Add(self.headSizer)
        self.mainSizer.Add(line, flag=wx.TOP, border = 3)
        self.mainSizer.Add(secLine, flag=wx.BOTTOM, border = 3)
        self.mainSizer.Add(self.actScroll)
        self.mainSizer.Add(lineBottom, flag=wx.TOP|wx.BOTTOM, border = 3)
        self.mainSizer.Add(self.okBtn, flag = wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, border = 10)

    def SetupHeadSection(self):
        # Sizer with combo boxes to define new action
        comboSizer = wx.BoxSizer()
        cmdChoices = []
        for c in CMD:
            cmdChoices.append(tr(c))
        self.cmdCombo = wx.ComboBox(self, -1, choices=cmdChoices, size=(134,26))
        self.cmdCombo.SetName('cmd')
        typeChoices = []
        for t in TYPE:
            typeChoices.append(tr(t))
        self.typeCombo = wx.ComboBox(self, -1, choices=typeChoices, size=(174,26))
        self.typeCombo.SetName('type')
        self.times = []
        for i in range(101):
            self.times.append(str(i))
        self.timeCombo = wx.ComboBox(self, -1, choices=self.times, size=(77,26))

        self.addBtn = wx.Button(self,-1,label="+", size=(25,25))

        self.Bind(wx.EVT_COMBOBOX, self.ComboSelection, self.cmdCombo)
        self.Bind(wx.EVT_COMBOBOX, self.ComboSelection, self.typeCombo)
        self.Bind(wx.EVT_COMBOBOX, self.ComboSelection, self.timeCombo)
        self.Bind(wx.EVT_BUTTON, self.AddAction, self.addBtn)

        comboSizer.Add(self.cmdCombo, flag = wx.LEFT, border = 10)
        comboSizer.Add(self.typeCombo)
        comboSizer.Add(self.timeCombo)
        comboSizer.Add(self.addBtn, flag = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border = 10)
        self.addBtn.Disable()
        self.ResetCombos()

        # Sizer with labels for the combo boxes
        labelSizer = wx.BoxSizer()

        cmdLabel = wx.StaticText(self,-1,label="Command:",size=(self.cmdCombo.GetSize()[0],17))
        triggerLabel = wx.StaticText(self,-1,label="Trigger:",size=(self.typeCombo.GetSize()[0],17))
        timeLabel = wx.StaticText(self,-1,label="Delay:")

        labelSizer.Add(cmdLabel, flag = wx.LEFT| wx.TOP, border = 6)
        labelSizer.Add(triggerLabel, flag = wx.TOP, border = 6)
        labelSizer.Add(timeLabel, flag = wx.TOP, border = 6)

        self.headSizer.Add(labelSizer)
        self.headSizer.Add(comboSizer)

    def ResetCombos(self):
        self.cmdCombo.SetSelection(-1)
        self.typeCombo.SetSelection(-1)
        self.timeCombo.SetSelection(-1)

    def LoadActionUI(self):
        for action in self.actions:
            self.__AddActionToUI(action)

    def __AddActionToUI(self, action):
        try:
            actionDict = ast.literal_eval(action)
            action = actionDict
        except:
            pass
        actBox = wx.BoxSizer()
        actBox.SetMinSize((409,10))
        desc = self.__GetDescription(action)

        descLabel = wx.StaticText(self.actScroll,-1,label=desc)
        descLabel.SetMinSize((385,25))
        delBtn = wx.Button(self.actScroll,-1,label="x",size=(25,25))
        line = wx.StaticLine(self.actScroll, -1, size = (416,2))
        self.Bind(wx.EVT_BUTTON, lambda event, action=action: self.DeleteAction(event,action), delBtn)

        actBox.Add(descLabel, flag = wx.ALL, border = 3)
        actBox.Add(delBtn, flag = wx.ALIGN_RIGHT | wx.ALL, border = 3)
        self.contentSizer.Prepend(line, flag = wx.ALL, border = 3)
        self.contentSizer.Prepend(actBox)
        self.contentSizer.Layout()
        self.actScroll.SetupScrolling(scroll_x=True, scroll_y=True)

    def __GetDescription(self, action):
        ind = CMD_CODE.index(action['command'])
        desc = '"' + tr(CMD[ind]) + '"'
        if action['type'] == ACTION_TYPE_PERIODIC:
            desc += " " + tr("every") + " " + action['periodic_interval']
            pType = action['periodic_type']
            if pType == PERIODIC_SEC:
                desc += " " + tr("sec")
            elif pType == PERIODIC_MIN:
                desc += " " + tr("min")
            elif pType == PERIODIC_HOUR:
                desc += " " + tr("hour")

            if int(action['periodic_interval']) > 1:
                desc += tr("desc_plural")
        elif action['type'] == ACTION_TYPE_ONETIME:
            desc += " " + tr("after")
            desc += " " + action['delay'] + " " + tr("sec")
            if int(action['delay']) > 1:
                desc += tr("desc_plural")
            desc += " " + tr("when")
            ind = TYPE_CODE.index(action['event'])
            event = tr(TYPE[ind])
            desc += " " + event
        return desc

    def ComboSelection(self, event=None):
        self.__ValidateInput()

    def DeleteAction(self, event, action):
        desc = self.__GetDescription(action)
        dlg = wx.MessageDialog(self, tr("delete_action") % desc, tr("deleting"), style = wx.YES_NO)
        if dlg.ShowModal() == wx.ID_YES:
            self.currentAction = action
            # send action to group master
            Publisher.subscribe(self.CurrentActionDeleted, 'action_deleted')
            Publisher.subscribe(self.UdpListenerStopped, 'listener_stop')
            self.prgDlg = wx.ProgressDialog(tr("deleting"), tr("deleting_action") % desc, parent=self, style=wx.PD_AUTO_HIDE)
            self.prgDlg.Pulse()
            msgData = network.messages.getMessage(GROUP_CONFIG_ACTION_DELETE, ["-s", str(action)])
            network.udpconnector.sendMessage(msgData, self.masterHost, 3)

    def CurrentActionDeleted(self):
        # if string and not dictionary --> convert
        self.currentAction = self.__toDict(self.currentAction)
        ind = self.__actionIndex(self.currentAction)
        if not ind == -1:
            del self.actions[ind]
        self.currentAction = None
        self.prgDlg.Update(100)
        if platform.system() == "Windows":
            self.prgDlg.Destroy()
        self.ResetCombos()
        self.contentSizer.Clear(True)
        self.LoadActionUI()

    def AddAction(self, event):
        action = self.InputToAction()
        self.currentAction = action
        self.SendCurrentActionToMaster()

    def InputToAction(self):
        cmd = CMD_CODE[self.cmdCombo.GetSelection()]
        type = TYPE_CODE[self.typeCombo.GetSelection()]
        time = self.times[self.timeCombo.GetSelection()]

        actType = ACTION_TYPE_PERIODIC
        if type in TYPE_ONETIME:
            actType = ACTION_TYPE_ONETIME

        action = {}
        action['type'] = actType
        if actType == ACTION_TYPE_PERIODIC:
            action['periodic_type'] = type
            action['periodic_interval'] = time
        else:
            action['event'] = type
            action['delay'] = time
        action['command'] = cmd
        return action

    def SendCurrentActionToMaster(self):
        if not self.currentAction == None:
            self.actionSaved = False
            # send action to group master
            Publisher.subscribe(self.CurrentActionSaved, 'action_saved')
            Publisher.subscribe(self.UdpListenerStopped, 'listener_stop')

            msgData = network.messages.getMessage(GROUP_CONFIG_ADD_ACTION, ["-s",str(self.currentAction)])
            network.udpconnector.sendMessage(msgData, self.masterHost, 3)

    def CurrentActionSaved(self):
        # group master responded that it received the action update
        self.actionSaved = True
        self.ResetCombos()
        self.actions.append(self.currentAction)
        self.__AddActionToUI(self.currentAction)
        self.currentAction = None


    def UdpListenerStopped(self):
        if not self.actionSaved:
            self.SendCurrentActionToMaster()


    def Close(self, event):
        self.MakeModal(False)
        self.Destroy()
        event.Skip()

    def __ValidateInput(self, event=None):
        if not self.cmdCombo.GetSelection() == -1 and not self.typeCombo.GetSelection() == -1 and not self.timeCombo.GetSelection() == -1:
            action = self.InputToAction()
            action = self.__toDict(action)
            if self.__actionIndex(action) == -1:
                self.addBtn.Enable()
            else:
                self.addBtn.Disable()
        else:
            self.addBtn.Disable()

    def __actionIndex(self,action):
        ind = -1
        cnt = 0
        # convert to dict in case it is still a string
        action = self.__toDict(action)
        action = self.__sortDict(action)
        for a in self.actions:
            a = self.__toDict(a)
            a = self.__sortDict(a)
            if cmp(a, action) == 0:
                ind = cnt
            cnt += 1
        return ind

    def __toDict(self,data):
        try:
            dict = ast.literal_eval(data)
            data = dict
        except:
            pass
        return data

    def __sortDict(self,dict):
        sDict = {}
        for key in sorted(dict):
            sDict[key] = dict[key]
        return sDict



def get_index(seq, attr, value):
    return next(index for (index, d) in enumerate(seq) if d[attr] == value)
