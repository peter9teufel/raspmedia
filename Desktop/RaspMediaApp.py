import packages.rmnetwork as network
from packages.rmnetwork.constants import *
import os, sys, ast, time
try:
	import wx
except ImportError:
	raise ImportError,"Wx Python is required."

class ConnectFrame(wx.Frame):
	def __init__(self,parent,id,title):
		wx.Frame.__init__(self,parent,id,title)
		self.parent = parent
		self.Bind(wx.EVT_CLOSE, self.close)
		self.mediaCtrlFrame = None
		self.hosts = []
		self.mainSizer = wx.GridBagSizer()
		self.initGui()
		self.searchHosts()

	def close(self, event):
		self.Destroy()
		sys.exit(0)

	def initGui(self):
		# Text label
		label = wx.StaticText(self,-1,label="Available RaspMedia Players:")
		self.mainSizer.Add(label,(0,0),(1,2),wx.EXPAND)
		
		label = wx.StaticText(self,-1,label="(double-click to connect)")
		self.mainSizer.Add(label,(1,0),(1,2),wx.EXPAND)

		id=wx.NewId()
		self.hostList=wx.ListCtrl(self,id,size=(300,200),style=wx.LC_REPORT|wx.SUNKEN_BORDER)
		self.hostList.Show(True)

		self.hostList.InsertColumn(0,"Host Address", width = 200)
		self.hostList.InsertColumn(1,"Port", width = 100)
		self.mainSizer.Add(self.hostList, (2,0))
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.HostListDoubleClicked, self.hostList)

		self.SetSizerAndFit(self.mainSizer)
		self.Center()
		self.Show(True)

	def HostFound(self, host):
		# self.hosts.Add(host)
		idx = self.hostList.InsertStringItem(0, host[0])

		port = str(host[1])
		print "Host insert in row " + str(idx) + ": " + host[0] + " - " + port
		self.hostList.SetStringItem(idx, 1, port)

	def searchHosts(self):
		# clear host list
		self.hostList.DeleteAllItems()
		network.udpresponselistener.registerObserver([OBS_HOST_SEARCH, self.HostFound])
		network.udpresponselistener.registerObserver([OBS_STOP, self.UdpListenerStopped])
		msgData = network.messages.getMessage(SERVER_REQUEST)
		dlgStyle =  wx.PD_AUTO_HIDE
		self.prgDialog = wx.ProgressDialog("Searching...", "Searching available RaspMedia Players...", maximum = 1, parent = self, style = dlgStyle)
		self.prgDialog.Pulse()
		network.udpconnector.sendMessage(msgData)

	def UdpListenerStopped(self):
		if self.prgDialog:
			self.prgDialog.Update(1)

	def HostListDoubleClicked(self, event):
		self.Hide()
		self.mediaCtrlFrame = RaspMediaCtrlFrame(self.parent,-1,'RaspMedia Control')
		self.mediaCtrlFrame.setHost(event.GetText())
		self.mediaCtrlFrame.Bind(wx.EVT_CLOSE, self.ChildFrameClosed)
		self.mediaCtrlFrame.Center()
		self.mediaCtrlFrame.Show(True)
		self.mediaCtrlFrame.LoadRemoteConfig(None)
		self.mediaCtrlFrame.LoadRemoteFileList(None)

	def ChildFrameClosed(self, event):
		self.mediaCtrlFrame.Destroy()
		self.Center()
		self.Show(True)
		self.searchHosts()
		pass


class RaspMediaCtrlFrame(wx.Frame):
	def __init__(self,parent,id,title):
		wx.Frame.__init__(self,parent,id,title)
		self.parent = parent
		self.path = os.getcwd()
		self.mainSizer = wx.GridBagSizer()
		self.configSizer = wx.GridBagSizer()
		self.playerSizer = wx.GridBagSizer()
		self.filesSizer = wx.GridBagSizer()
		self.prgDialog = None
		self.initialize()

	def setHost(self, hostAddress):
		self.host = hostAddress

	def initialize(self):

		self.SetupMenuBar()
		self.SetupFileLists()
		self.SetupPlayerSection()
		self.SetupConfigSection()
		# Text Entry
		# self.entry = wx.TextCtrl(self,-1,value=u"Enter text here...",style=wx.TE_PROCESS_ENTER)
		# sizer.Add(self.entry,(0,0),(1,1),wx.EXPAND)
		# self.Bind(wx.EVT_TEXT_ENTER, self.OnPressEnter, self.entry)

		# Text label
		#self.label = wx.StaticText(self,-1,label="Hello!")
		#self.label.SetBackgroundColour(wx.BLUE)
		#self.label.SetForegroundColour(wx.WHITE)
		#sizer.Add(self.label,(1,0),(1,2),wx.EXPAND)
		
		self.mainSizer.Add(self.playerSizer,(0,0))
		self.mainSizer.Add(self.configSizer, (0,1), flag=wx.ALIGN_CENTER)
		self.mainSizer.Add(self.filesSizer, (2,0), span=(1,2))

		self.SetSizerAndFit(self.mainSizer)
		# self.SetSizeHints(self.GetSize().x,self.GetSize().y,-1,self.GetSize().y)
		self.Show(True)

	def SetupPlayerSection(self):
		# Text label
		label = wx.StaticText(self,-1,label="Remote Control:")
		self.playerSizer.Add(label,(0,0),(1,2),wx.EXPAND)
		
		# Play and Stop Button
		button = wx.Button(self,-1,label="Play")
		self.playerSizer.Add(button,(1,0))
		self.Bind(wx.EVT_BUTTON, self.playClicked, button)

		button = wx.Button(self,-1,label="Stop")
		self.playerSizer.Add(button,(2,0))
		self.Bind(wx.EVT_BUTTON, self.stopClicked, button)

	def SetupConfigSection(self):
		self.cbImgEnabled = wx.CheckBox(self, -1, "Enable Images")
		self.cbVidEnabled = wx.CheckBox(self, -1, "Enable Videos")
		self.cbAutoplay = wx.CheckBox(self, -1, "Autoplay")
		self.cbRepeat = wx.CheckBox(self, -1, "Repeat")

		# set names for further identifying
		self.cbImgEnabled.SetName('image_enabled')
		self.cbVidEnabled.SetName('video_enabled')
		self.cbAutoplay.SetName('autoplay')
		self.cbRepeat.SetName('repeat')

		self.Bind(wx.EVT_CHECKBOX, self.CheckboxToggled, self.cbImgEnabled)
		self.Bind(wx.EVT_CHECKBOX, self.CheckboxToggled, self.cbVidEnabled)
		self.Bind(wx.EVT_CHECKBOX, self.CheckboxToggled, self.cbAutoplay)
		self.Bind(wx.EVT_CHECKBOX, self.CheckboxToggled, self.cbRepeat)

		self.configSizer.Add(wx.StaticText(self,-1,label="Configuration:"),(0,0))
		self.configSizer.Add(self.cbImgEnabled, (1,0))
		self.configSizer.Add(self.cbVidEnabled, (2,0))
		self.configSizer.Add(self.cbAutoplay, (1,1))
		self.configSizer.Add(self.cbRepeat, (2,1))
		pass

	def SetupFileLists(self):
		# local list
		self.AddLocalList()
		self.AddRemoteList()

		button = wx.Button(self,-1,label="Change directory")
		self.filesSizer.Add(button,(1,0))
		self.Bind(wx.EVT_BUTTON, self.ChangeDir, button)
		button = wx.Button(self,-1,label="Refresh remote filelist")
		self.filesSizer.Add(button,(1,1))
		self.Bind(wx.EVT_BUTTON, self.LoadRemoteFileList, button)

	def AddLocalList(self):
		id=wx.NewId()
		self.localList=wx.ListCtrl(self,id,size=(300,400),style=wx.LC_REPORT|wx.SUNKEN_BORDER)
		self.localList.Show(True)

		self.localList.InsertColumn(0,"Local Files: " + self.path, width = 298)
		self.filesSizer.Add(self.localList, (0,0))
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.LocalFileDoubleClicked, self.localList)
		self.UpdateLocalFiles()

	def AddRemoteList(self):
		id=wx.NewId()
		self.remoteList=wx.ListCtrl(self,id,size=(300,400),style=wx.LC_REPORT|wx.SUNKEN_BORDER)
		self.remoteList.Show(True)
		self.remoteList.InsertColumn(0,"Remote Files: ", width = 298)	
		self.filesSizer.Add(self.remoteList, (0,1))
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.RemoteFileDoubleClicked, self.remoteList)

	def UpdateLocalFiles(self):
		self.localList.DeleteAllItems()
		for file in os.listdir(self.path):
			if not file.startswith('.') and '.' in file:
				self.localList.InsertStringItem(self.localList.GetItemCount(), file)

	def InsertReceivedFileList(self, serverAddr, files):
		self.remoteList.DeleteAllItems()
		files.sort()
		for file in files:
			if not file.startswith('.') and '.' in file:
				self.remoteList.InsertStringItem(self.remoteList.GetItemCount(), file)

	def SetupMenuBar(self):
		# menus
		fileMenu = wx.Menu()

		#FILE MENU
		menuOpen = fileMenu.Append(wx.ID_OPEN, "&Change directory"," Change directory")  #add open to File
		menuExit = fileMenu.Append(wx.ID_EXIT, "&Exit"," Terminate the program")  #add exit to File
		self.Bind(wx.EVT_MENU, self.ChangeDir, menuOpen)
		#MENUBAR
		menuBar = wx.MenuBar()
		menuBar.Append(fileMenu,"&File") # Adding the "filemenu" to the MenuBar

		self.SetMenuBar(menuBar)

	def UpdateConfigUI(self, config):
		print "Update CONFIG METHOD"
		configDict = ast.literal_eval(config)
		print configDict
		self.cbImgEnabled.SetValue(configDict['image_enabled'])
		self.cbVidEnabled.SetValue(configDict['video_enabled'])
		self.cbRepeat.SetValue(configDict['repeat'])
		self.cbAutoplay.SetValue(configDict['autoplay'])

	def LocalFileDoubleClicked(self, event):
		filePath = self.path + '/' +  event.GetText()
		print "File: ", filePath
		network.tcpfileclient.registerObserver(self.LoadRemoteFileList)
		network.tcpfileclient.sendFile(filePath, self.host, self)
		#self.LoadRemoteFileList(None)

	def RemoteFileDoubleClicked(self, event):
		fileName = event.GetText()
		filePath = self.path + '/' +  fileName
		# dialog to verify deleting file on player
		msg = "Delete the file '" + fileName + "' from the player (will stop and restart player)? This can not be undone!"
		dlg = wx.MessageDialog(self, msg, "Delete file from player?", wx.YES_NO | wx.ICON_EXCLAMATION)
		if dlg.ShowModal() == wx.ID_YES:
			dlgStyle =  wx.PD_AUTO_HIDE
			self.prgDialog = wx.ProgressDialog("Deleting file...", "Deleting file from player...", maximum = 1, parent = self, style = dlgStyle)
			self.prgDialog.Pulse()
			msgData = network.messages.getMessage(DELETE_FILE, ["-s", str(fileName)])
			network.udpconnector.sendMessage(msgData, self.host)
			time.sleep(3)
			self.prgDialog.Update(1, "Done!")
			self.LoadRemoteFileList(None)
		dlg.Destroy()

	def CheckboxToggled(self, event):
		checkbox = event.GetEventObject()
		print checkbox.GetName()
		msgData = network.messages.getConfigUpdateMessage(checkbox.GetName(), checkbox.IsChecked())
		network.udpconnector.sendMessage(msgData, self.host)
		#print "Checkbox toggled: ", event.GetEventObject().GedId()
		pass

	def ChangeDir(self, event):
		dlg = wx.DirDialog(self, message="Select a directory that contains images or videos you would like to browse and upload to your media player.", defaultPath=self.path, style=wx.DD_CHANGE_DIR)


		# Call the dialog as a model-dialog so we're required to choose Ok or Cancel
		if dlg.ShowModal() == wx.ID_OK:
			# User has selected something, get the path, set the window's title to the path
			filename = dlg.GetPath()
			print filename
			self.path = filename
			self.UpdateLocalFiles()
		dlg.Destroy() # we don't need the dialog any more so we ask it to clean-up

	def LoadRemoteFileList(self, event):
		network.udpresponselistener.registerObserver([OBS_FILE_LIST, self.InsertReceivedFileList])
		network.udpresponselistener.registerObserver([OBS_STOP, self.UdpListenerStopped])
		msgData = network.messages.getMessage(FILELIST_REQUEST)
		dlgStyle =  wx.PD_AUTO_HIDE
		self.prgDialog = wx.ProgressDialog("Loading...", "Loading filelist from player...", maximum = 1, parent = self, style = dlgStyle)
		self.prgDialog.Pulse()
		network.udpconnector.sendMessage(msgData, self.host)

	def LoadRemoteConfig(self, event):
		network.udpresponselistener.registerObserver([OBS_CONFIG, self.UpdateConfigUI])
		network.udpresponselistener.registerObserver([OBS_STOP, self.UdpListenerStopped])
		msgData = network.messages.getMessage(CONFIG_REQUEST)
		dlgStyle =  wx.PD_AUTO_HIDE
		self.prgDialog = wx.ProgressDialog("Loading...", "Loading configuration from player...", maximum = 1, parent = self, style = dlgStyle)
		self.prgDialog.Pulse()
		network.udpconnector.sendMessage(msgData, self.host)

	def UdpListenerStopped(self):
		if self.prgDialog:
			self.prgDialog.Update(1)

	def playClicked(self, event):
		msgData = network.messages.getMessage(PLAYER_START)
		network.udpconnector.sendMessage(msgData, self.host)

	def stopClicked(self, event):
		msgData = network.messages.getMessage(PLAYER_STOP)
		network.udpconnector.sendMessage(msgData, self.host)


# MAIN ROUTINE
if __name__ == '__main__':
	app = wx.App()
	# frame = RaspMediaCtrlFrame(None, -1, 'RaspMedia Control')
	frame = ConnectFrame(None, -1, 'RaspMedia Control')
	app.MainLoop()