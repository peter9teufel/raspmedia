import packages.rmnetwork as network
import packages.rmutil as rmutil
from packages.rmnetwork.constants import *
import os, sys, platform, ast, time, threading, shutil
from wx.lib.pubsub import pub as Publisher
from wx.lib.wordwrap import wordwrap
try:
	import wx
except ImportError:
	raise ImportError,"Wx Python is required."

playerCount = 0
activePage = 0
HOST_WIN = 1
HOST_MAC = 2
HOST_LINUX = 3
HOST_SYS = None
BASE_PATH = None


################################################################################
# MAIN FRAME OF APPLICATION ####################################################
################################################################################
class AppFrame(wx.Frame):
	def __init__(self,parent,id,title):
		wx.Frame.__init__(self,parent,id,title,size=(600,600))
		global playerCount
		self.parent = parent
		self.Bind(wx.EVT_CLOSE, self.Close)
		self.SetupMenuBar()
		print "Initializing Notebook..."
		self.notebook = RemoteNotebook(self,-1,None)
		print "Showing window..."
		self.Center()
		self.Show()
		print "Starting host search..."
		self.notebook.SearchHosts()

	def Close(self, event=None):
		global playerCount
		Publisher.unsubAll()
		playerCount = 0
		self.notebook.Close()
		network.udpresponselistener.destroy()
		self.Destroy()
		sys.exit(0)

	def SetupMenuBar(self):
		# menus
		fileMenu = wx.Menu()
		helpMenu = wx.Menu()

		# File Menu
		menuSettings = fileMenu.Append(wx.ID_ANY, "&Player Settings", "Player Settings")
		menuExit = fileMenu.Append(wx.ID_EXIT, "&Exit"," Terminate the program")
		self.Bind(wx.EVT_MENU, self.Close, menuExit)
		self.Bind(wx.EVT_MENU, self.ShowPlayerSettings, menuSettings)

		# Help Menu
		about = helpMenu.Append(wx.ID_ANY, "&About")
		self.Bind(wx.EVT_MENU, self.ShowAbout, about)

		# Menubar
		menuBar = wx.MenuBar()
		menuBar.Append(fileMenu, "&File") # Adding the "filemenu" to the MenuBar

		menuBar.Append(helpMenu, "&About")
		self.SetMenuBar(menuBar)

	def ShowAbout(self, event):
		# message read from defined version info file in the future
		msg = "RaspMedia Control v1.0\n(c) 2014 by www.multimedia-installationen.at\nContact: software@multimedia-installationen.at\nAll rights reserved."
		dlg = wx.MessageDialog(self, msg, "About", style=wx.OK)
		dlg.ShowModal()

	def ShowPlayerSettings(self, event):
		settings = SettingsFrame(self,-1,"Player Settings",self.notebook.CurrentlyActiveHost(), self.notebook.CurrentConfig())
		settings.Center()
		settings.SetBackgroundColour('WHITE')
		settings.Refresh()
		settings.Show()

	def SettingsClosedWithConfig(self, config):
		self.notebook.UpdateCurrentPlayerUI(config)



################################################################################
# SETTINGS FRAME ###############################################################
################################################################################
class SettingsFrame(wx.Frame):
	def __init__(self,parent,id,title,host,config):
		wx.Frame.__init__(self,parent,id,title,size=(400,300))
		self.parent = parent
		self.Bind(wx.EVT_CLOSE, self.Close)
		self.host = host['addr']
		self.name = host['name']
		self.prgDialog = None
		self.Initialize()
		self.SetSizerAndFit(self.configSizer)
		self.Show()
		self.UpdateUI(config, True)

	def Close(self, event=None):
		Publisher.unsubAll()
		self.parent.SettingsClosedWithConfig(self.config)
		self.Destroy()

	def Initialize(self):
		self.configSizer = wx.GridBagSizer()
		# checkboxes
		self.cbImgEnabled = wx.CheckBox(self, -1, "Enable Images")
		self.cbVidEnabled = wx.CheckBox(self, -1, "Enable Videos")
		self.cbAutoplay = wx.CheckBox(self, -1, "Autoplay")
		self.cbRepeat = wx.CheckBox(self, -1, "Repeat")

		# interval, player name and ip
		intervalLabel = wx.StaticText(self,-1,label="Image interval:")
		self.imgIntervalLabel = wx.StaticText(self,-1,label="")
		nameLabel = wx.StaticText(self,-1,label="Player name:")
		self.playerNameLabel = wx.StaticText(self,-1,label="")
		addrLabel = wx.StaticText(self,-1,label="IP-Address:")
		playerAddr = wx.StaticText(self,-1,label=self.host)

		updateBtn = wx.Button(self, -1, "Update player")

		self.editInterval = wx.Button(self,-1,label="...",size=(27,25))
		self.editName = wx.Button(self,-1,label="...",size=(27,25))

		# horizontal divider line
		line = wx.StaticLine(self,-1,size=(260,2))

        # set names for further identifying
		self.cbImgEnabled.SetName('image_enabled')
		self.cbVidEnabled.SetName('video_enabled')
		self.cbAutoplay.SetName('autoplay')
		self.cbRepeat.SetName('repeat')
		self.editInterval.SetName('btn_image_interval')
		self.editName.SetName('btn_player_name')
		updateBtn.SetName('btn_update')

		# bind UI element events
		self.Bind(wx.EVT_CHECKBOX, self.CheckboxToggled, self.cbImgEnabled)
		self.Bind(wx.EVT_CHECKBOX, self.CheckboxToggled, self.cbVidEnabled)
		self.Bind(wx.EVT_CHECKBOX, self.CheckboxToggled, self.cbAutoplay)
		self.Bind(wx.EVT_CHECKBOX, self.CheckboxToggled, self.cbRepeat)
		self.Bind(wx.EVT_BUTTON, self.ButtonClicked, self.editInterval)
		self.Bind(wx.EVT_BUTTON, self.ButtonClicked, self.editName)
		self.Bind(wx.EVT_BUTTON, self.ButtonClicked, updateBtn)

		self.configSizer.Add(self.cbImgEnabled, (0,0), flag=wx.TOP | wx.LEFT, border = 5)
		self.configSizer.Add(self.cbVidEnabled, (1,0), flag=wx.LEFT, border = 5)
		self.configSizer.Add(self.cbAutoplay, (0,1), flag=wx.TOP, border = 5)
		self.configSizer.Add(self.cbRepeat, (1,1))
		self.configSizer.Add(intervalLabel, (3,0), flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 5)
		self.configSizer.Add(self.imgIntervalLabel, (3,1), flag=wx.ALIGN_CENTER_VERTICAL)
		self.configSizer.Add(self.editInterval, (3,3))
		self.configSizer.Add(nameLabel, (4,0), flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 5)
		self.configSizer.Add(self.playerNameLabel, (4,1), flag=wx.ALIGN_CENTER_VERTICAL)
		self.configSizer.Add(self.editName, (4,3))
		self.configSizer.Add(addrLabel, (5,0), flag = wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.BOTTOM, border = 5)
		self.configSizer.Add(playerAddr, (5,1), flag = wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM, border = 5)
		self.configSizer.Add(updateBtn, (0,4), flag = wx.ALL, border = 5)
		self.configSizer.Add(line, (2,0), span=(1,5), flag=wx.TOP | wx.BOTTOM, border=5)


	def UpdateUI(self, config, isDict=False):
		if isDict:
			configDict = config
		else:
			configDict = ast.literal_eval(config)
		self.config = configDict
		self.cbImgEnabled.SetValue(configDict['image_enabled'])
		self.cbVidEnabled.SetValue(configDict['video_enabled'])
		self.cbRepeat.SetValue(configDict['repeat'])
		self.cbAutoplay.SetValue(configDict['autoplay'])
		self.imgIntervalLabel.SetLabel(str(configDict['image_interval']))
		self.playerNameLabel.SetLabel(str(configDict['player_name']))

	def LoadConfig(self):
		Publisher.subscribe(self.UpdateUI, 'config')
		Publisher.subscribe(self.UdpListenerStopped, 'listener_stop')
		print "Observers registered..."
		msgData = network.messages.getMessage(CONFIG_REQUEST)
		dlgStyle =  wx.PD_AUTO_HIDE
		#self.prgDialog = wx.ProgressDialog("Loading...", "Loading configuration from player...", maximum = 0, parent = self, style = dlgStyle)
		#self.prgDialog.Pulse()
		network.udpconnector.sendMessage(msgData, self.host)

	def UdpListenerStopped(self):
		if self.prgDialog:
			self.prgDialog.Update(100)
			self.prgDialog.Destroy()
			#self.prgDialog = None

	def ButtonClicked(self, event):
		button = event.GetEventObject()
		if button.GetName() == 'btn_image_interval':
			dlg = wx.TextEntryDialog(self, "New Interval:", "Image Interval", self.imgIntervalLabel.GetLabel())
			if dlg.ShowModal() == wx.ID_OK:
				try:
					newInterval = int(dlg.GetValue())
					# self.imgIntervalLabel.SetLabel(str(newInterval))
					msgData = network.messages.getConfigUpdateMessage("image_interval", newInterval)
					network.udpconnector.sendMessage(msgData, self.host)
					time.sleep(0.2)
					self.LoadConfig()
				except Exception, e:
					error = wx.MessageDialog(self, "Please enter a valid number!", "Invalid interval", wx.OK | wx.ICON_EXCLAMATION)
					error.ShowModal()

			dlg.Destroy()
		elif button.GetName() == 'btn_player_name':
			dlg = wx.TextEntryDialog(self, "New name:", "Player Name", self.playerNameLabel.GetLabel())
			if dlg.ShowModal() == wx.ID_OK:
				newName = dlg.GetValue()
				self.playerNameLabel.SetLabel(newName)
				msgData = network.messages.getConfigUpdateMessage("player_name", str(newName))
				network.udpconnector.sendMessage(msgData, self.host)
				time.sleep(0.2)
				self.LoadConfig()
			dlg.Destroy()
		elif button.GetName() == 'btn_update':
			# register observer
			network.udpresponselistener.registerObserver([OBS_UPDATE, self.OnPlayerUpdated])
			network.udpresponselistener.registerObserver([OBS_STOP, self.UdpListenerStopped])

			self.prgDialog = wx.ProgressDialog("Updating...", "Player is trying to update, please stand by...")
			#self.prgDialog.ShowModal()
			self.prgDialog.Pulse()

			msgData = network.messages.getMessage(PLAYER_UPDATE)
			network.udpconnector.sendMessage(msgData, self.host, UDP_UPDATE_TIMEOUT)

	def CheckboxToggled(self, event):
		checkbox = event.GetEventObject()
		print checkbox.GetName()
		msgData = network.messages.getConfigUpdateMessage(checkbox.GetName(), checkbox.IsChecked())
		network.udpconnector.sendMessage(msgData, self.host)
		self.LoadConfig()

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
		print "Player found - initializing panel..."

		# add page for found Player
		#page = RaspMediaCtrlPanel(self,-1,playerName,playerCount,host[0])
		#print "Appending page to list..."
		#self.pages.append(page)
		#print "Adding page to notebook..."
		#self.AddPage(page, playerName)

		print "Adding host to list..."
		if not self.HostInList(host[0], playerName):
			self.hosts.append({"addr": host[0], "name": playerName})
			playerCount += 1
		#print "Fitting window..."
		#self.Fit()
		#self.parent.Fit()

	def HostInList(self, addr, playerName):
		for h in self.hosts:
			if h['addr'] == addr and h['name'] == playerName:
				return True
		return False

	def SearchHosts(self):
		self.hostSearch = True
		#network.udpresponselistener.registerObserver([OBS_HOST_SEARCH, self.HostFound])
		Publisher.subscribe(self.HostFound, 'host_found')
		Publisher.subscribe(self.UdpListenerStopped, 'listener_stop')
		#network.udpresponselistener.registerObserver([OBS_STOP, self.UdpListenerStopped, self])
		msgData = network.messages.getMessage(SERVER_REQUEST)
		self.prgDialog = wx.ProgressDialog("Searching...", "Searching available RaspMedia Players...", parent = self, style = wx.PD_AUTO_HIDE)
		self.prgDialog.Pulse()
		network.udpconnector.sendMessage(msgData)

	def LoadPageData(self, pageNumber):
		print "Loading config and remote list for page ", pageNumber
		self.GetPage(pageNumber).LoadData()
		#self.GetPage(pageNumber).pageDataLoading = True
		#self.GetPage(pageNumber).LoadRemoteConfig()
		#self.GetPage(pageNumber).LoadRemoteFileList()

	def UdpListenerStopped(self):
		global playerCount
		Publisher.unsubscribe(self.UdpListenerStopped, 'listener_stop')
		Publisher.unsubscribe(self.HostFound, 'host_found')
		print "Number of observers: ", len(network.udpresponselistener.observers)
		print "Number of players found: ", playerCount
		if self.hostSearch:
			self.hostSearch = False
			if playerCount == 0:
				self.prgDialog.Update(100)
				if HOST_SYS == HOST_WIN:
					self.prgDialog.Destroy()
				# dlg = wx.MessageDialog(self,"No RaspMedia Players found, check if your players are running and connected to the local network, restart the application to try again.", "No Player found", style = wx.OK)
				dlg = wx.SingleChoiceDialog(self,wordwrap("No RaspMedia Players found, check if your players are running and connected to the local network.", 300, wx.ClientDC(self)), "No Player found", ['Rescan', 'Exit'])
				result = dlg.ShowModal()
				selection = dlg.GetSelection()
				print "RESULT: ", result
				if result == wx.ID_OK:
					print "OK clicked, checking selected index... ", selection
					if selection == 0: # RESCAN
						self.SearchHosts()
					#elif selection == 1:
					#	pass
					elif selection == 1: # EXIT
						self.parent.Close()
				elif result == wx.ID_CANCEL:
					print "Cancel clicked, terminating program, bye bye..."
					self.parent.Close()
			else:
				#self.prgDialog.Destroy()
				ind = 0
				for host in self.hosts:
					print "Preparing page for " + host['name']
					print "Player address: " + host['addr']
					curPage = RaspMediaCtrlPanel(self,-1,host['name'],ind,host['addr'])
					self.pages.append(curPage)
					self.AddPage(curPage, host['name'])
					ind += 1
				self.LoadPageData(0)
				self.Fit()
				self.parent.Fit()
				if HOST_SYS == HOST_WIN:
					self.parent.SetSize((self.GetSize()[0]-85, self.GetSize()[1]+35))
				else:
					self.parent.SetSize((self.GetSize()[0]-53, self.GetSize()[1]))
				self.parent.Center()

	def OnPageChanged(self, event):
		global HOST_SYS
		print "ON PAGE CHANGED TRIGGER"
		self.activePageNr = event.GetSelection()
		if HOST_SYS == HOST_LINUX and event.GetOldSelection() == -1:
			pass
		else:
			# pass event to all pages, appropriate one will load data
			for page in self.pages:
				page.PageChanged(event)


################################################################################
# RASP MEDIA CONTROL PANEL #####################################################
################################################################################
class RaspMediaCtrlPanel(wx.Panel):
	def __init__(self,parent,id,title,index,host):
		#wx.Panel.__init__(self,parent,id,title)
		wx.Panel.__init__(self,parent,-1)
		self.parent = parent
		self.index = index
		self.host = host
		self.path = self.DefaultPath()
		self.mainSizer = wx.GridBagSizer()
		self.configSizer = wx.GridBagSizer()
		self.playerSizer = wx.GridBagSizer()
		self.filesSizer = wx.GridBagSizer()
		self.notebook_event = None
		self.prgDialog = None
		self.pageDataLoading = False
		self.remoteListLoading = False
		self.Initialize()

	def DefaultPath(self):
		path = os.path.expanduser("~")
		result = path
		# try common image directory paths
		if os.path.isdir(path + '/Bilder'):
			result = path + '/Bilder'
		elif os.path.isdir(path + '/Eigene Bilder'):
			result = path + '/Eigene Bilder'
		elif os.path.isdir(path + '/Pictures'):
			result = path + '/Pictures'
		elif os.path.isdir(path + '/Images'):
			result = path + '/Images'
		return result

	def SetHost(self, hostAddress):
		self.host = hostAddress

	def LoadData(self):
		self.pageDataLoading = True
		self.remoteListLoading = False
		# subscribe for async callbacks
		Publisher.subscribe(self.UpdateConfigUI, 'config')
		Publisher.subscribe(self.InsertReceivedFileList, 'remote_files')
		Publisher.subscribe(self.UdpListenerStopped, 'listener_stop')
		# start loading data
		self.prgDialog = wx.ProgressDialog("Loading...", "Loading configuration and filelist from player...")
		self.prgDialog.Pulse()
		self.LoadRemoteConfig()

	def PageChanged(self, event):
		old = event.GetOldSelection()
		new = event.GetSelection()
		sel = self.parent.GetSelection()
		self.notebook_event = event
		print "OnPageChanged, old:%d, new:%d, sel:%d" % (old, new, sel)
		newPage = self.parent.GetPage(new)
		if self.index == newPage.index:
			print "PAGE CHANGED TO INDEX %d - PROCESSING AND LOADING DATA..." % (self.index)
			self.pageDataLoading = True
			self.LoadData()

	def Initialize(self):
		print "Setting up player section..."
		self.SetupPlayerSection()
		#print "Setting up config section..."
		#self.SetupConfigSection()
		print "Setting up file lists..."
		self.SetupFileLists()

		self.mainSizer.Add(self.playerSizer,(0,0), flag=wx.ALIGN_CENTER_HORIZONTAL | wx.LEFT | wx.RIGHT, border=10)
		self.mainSizer.Add(self.configSizer, (0,2), flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, border=10)

		self.mainSizer.Add(self.filesSizer, (2,0), span=(1,4), flag=wx.BOTTOM | wx.LEFT | wx.RIGHT, border=10)

		self.SetSizerAndFit(self.mainSizer)

		line = wx.StaticLine(self,-1,size=(self.mainSizer.GetSize()[0],2))
		self.mainSizer.Add(line, (1,0), span=(1,4))

		line = wx.StaticLine(self,-1,size=(2,self.mainSizer.GetCellSize(0,0)[1]),style=wx.LI_VERTICAL)
		self.mainSizer.Add(line,(0,1), flag = wx.LEFT, border = 10)

		self.Fit()
		psHeight = self.playerSizer.GetSize()[1]
		print "PlayerSizer height: ",psHeight
		line = wx.StaticLine(self,-1,size=(2,psHeight),style=wx.LI_VERTICAL)
		self.playerSizer.Add(line,(0,2), span=(3,1), flag=wx.LEFT | wx.RIGHT, border=5)

		# self.SetSizeHints(self.GetSize().x,self.GetSize().y,-1,self.GetSize().y)
		#self.SetSizerAndFit(self.mainSizer)
		self.Show(True)

	def SetupPlayerSection(self):
		# Text label
		label = wx.StaticText(self,-1,label="Remote Control:")
		self.playerSizer.Add(label,(0,0),(1,2), flag = wx.TOP | wx.BOTTOM, border=5)

		# player name and address
		nameLabel = wx.StaticText(self,-1,label="Player name: ")
		self.playerNameLabel = wx.StaticText(self,-1,label="", size = (130,nameLabel.GetSize()[1]))
		addrLabel = wx.StaticText(self,-1,label="IP-Address: ")
		playerAddr = wx.StaticText(self,-1,label=self.host)
		self.playerSizer.Add(nameLabel, (1,0), flag=wx.ALIGN_CENTER_VERTICAL)
		self.playerSizer.Add(self.playerNameLabel, (1,1), flag=wx.ALIGN_CENTER_VERTICAL)
		self.playerSizer.Add(addrLabel, (2,0), flag = wx.ALIGN_CENTER_VERTICAL)
		self.playerSizer.Add(playerAddr, (2,1), flag = wx.ALIGN_CENTER_VERTICAL)

		# Play and Stop Button
		button = wx.Button(self,-1,label="Play")
		self.playerSizer.Add(button,(1,3))
		self.Bind(wx.EVT_BUTTON, self.PlayClicked, button)

		button = wx.Button(self,-1,label="Stop")
		self.playerSizer.Add(button,(2,3), flag=wx.TOP, border=5)
		self.Bind(wx.EVT_BUTTON, self.StopClicked, button)

		button = wx.Button(self,-1,label="Identify")
		button.SetName("btn_identify")
		self.playerSizer.Add(button,(1,5), flag = wx.BOTTOM, border = 5)
		self.Bind(wx.EVT_BUTTON, self.ButtonClicked, button)

		button = wx.Button(self,-1,label="Reboot")
		button.SetName("btn_reboot")
		self.playerSizer.Add(button,(2,5), flag=wx.TOP | wx.BOTTOM, border=5)
		self.Bind(wx.EVT_BUTTON, self.ButtonClicked, button)

	def SetupFileLists(self):
		self.filesSizer.SetEmptyCellSize((0,0))
		# setup file lists and image preview
		print "Adding local list..."
		self.AddLocalList()
		print "Adding image preview..."
		self.AddImagePreview()
		print "Adding remote list..."
		self.AddRemoteList()

		#imageFile = resource_path("img/ic_folder_select.png")
		#btnIcon = wx.Image(imageFile, wx.BITMAP_TYPE_ANY)
		#btnIcon = btnIcon.Scale(30,30)
		#btnIcon = btnIcon.ConvertToBitmap()
		#selectFolder = wx.BitmapButton(self, id=-1, bitmap=btnIcon, pos=(7,7), size=(44,44))
		selectFolder = wx.Button(self,-1,label="Select directory...")
		self.filesSizer.Add(selectFolder, (0,0), flag = wx.TOP | wx.BOTTOM, border = 5)
		self.Bind(wx.EVT_BUTTON, self.ChangeDir, selectFolder)

		button = wx.Button(self,-1,label="Refresh remote filelist")
		self.filesSizer.Add(button,(3,0))
		self.Bind(wx.EVT_BUTTON, self.LoadRemoteFileList, button)
		self.filesSizer.Fit(self)

	def AddLocalList(self):
		print "Initializing empty local lists..."
		self.localList = wx.ListCtrl(self,-1,size=(400,200),style=wx.LC_REPORT|wx.SUNKEN_BORDER)
		print "Showing list..."
		self.localList.Show(True)
		self.localList.InsertColumn(0,"Filename", width = 300)
		self.localList.InsertColumn(1,"Filesize", width = 80, format = wx.LIST_FORMAT_RIGHT)
		self.filesSizer.Add(self.localList, (1,0), span=(1,1))
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.LocalFileDoubleClicked, self.localList)
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.LocalFileSelected, self.localList)
		self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.LocalFileRightClicked, self.localList)
		self.UpdateLocalFiles()

	def AddImagePreview(self):
		img = wx.EmptyImage(200,200)
		self.imageCtrl = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(img))
		self.SetPreviewImage('img/preview.png')
		self.filesSizer.Add(self.imageCtrl, (1,1), flag = wx.LEFT, border=5)

	def AddRemoteList(self):
		print "Initializing empty remote lists..."
		self.remoteList=wx.ListCtrl(self,-1,size=(600,200),style=wx.LC_REPORT|wx.SUNKEN_BORDER)
		self.remoteList.Show(True)
		self.remoteList.InsertColumn(0,"Remote Files: ", width = 598)
		self.filesSizer.Add(self.remoteList, (2,0), span=(1,2), flag = wx.EXPAND | wx.TOP, border = 10)
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.RemoteFileDoubleClicked, self.remoteList)
		self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.RemoteFileRightClicked, self.remoteList)

	def UpdateLocalFiles(self):
		self.localList.DeleteAllItems()

		if not self.path.endswith(':') or not len(self.path <= 1):
			self.localList.InsertStringItem(0, '..')

		folders = []
		files = []
		for file in os.listdir(self.path):
			if not file.startswith(('$','.')):
				imgOrVideo = file.endswith((SUPPORTED_IMAGE_EXTENSIONS)) or file.endswith((SUPPORTED_VIDEO_EXTENSIONS))
				if imgOrVideo:
					files.append({"filename": file, "size": os.stat(self.path + '/' + file).st_size})
				elif os.path.isdir(self.path + '/' + file):
					folders.append(file)

		for folderName in folders:
			self.localList.InsertStringItem(self.localList.GetItemCount(), folderName)

		for curFile in files:
			idx = self.localList.InsertStringItem(self.localList.GetItemCount(), curFile['filename'])
			size = curFile['size']
			size = round(size / 1024 / 1024.0, 1)
			sizeStr = str(size) + "MB"
			self.localList.SetStringItem(idx, 1, sizeStr)

		#col = self.localList.GetColumn(0)
		#col.SetText(self.path)
		#self.localList.SetColumn(0, col)

	def InsertReceivedFileList(self, serverAddr, files):
		print "UPDATING REMOTE FILELIST UI..."
		self.remoteList.DeleteAllItems()
		files.sort()
		for file in reversed(files):
			if not file.startswith('.') and '.' in file:
				self.remoteList.InsertStringItem(0, file)

	def UpdateConfigUI(self, config, isDict=False):
		global HOST_SYS
		if isDict:
			configDict = config
		else:
			configDict = ast.literal_eval(config)
		print configDict
		self.config = configDict
		self.playerNameLabel.SetLabel(configDict['player_name'])
		#if self.notebook_event:
		#	self.parent.SetPageText(self.notebook_event.GetSelection(), str(configDict['player_name']))
		#else:
		self.parent.SetPageText(self.parent.GetSelection(), str(configDict['player_name']))
		self.parent.parent.Refresh()

	def GetLocalSelectionInfo(self):
		mixed = False
		prevType = None
		index = self.localList.GetFirstSelected()
		cnt = 0
		while not index == -1:
			item = self.localList.GetItem(index,0)
			filePath = self.path + '/' + item.GetText()
			curType = None
			if filePath.endswith((SUPPORTED_VIDEO_EXTENSIONS)) or filePath.endswith((SUPPORTED_IMAGE_EXTENSIONS)):
				curType = 'media'
			elif os.path.isdir(filePath):
				curType = 'dir'
			if prevType and curType and not curType == prevType:
				mixed = True
			cnt += 1
			index = self.localList.GetNextSelected(index)
		if mixed:
			resType = "mixed"
		else:
			resType = curType
		return {"count": cnt, "type": resType}

	def MutlipleLocalFilesSelected(self):
		index = self.localList.GetFirstSelected()
		if index == -1:
			return False
		else:
			if self.localList.GetNextSelected(index) == -1:
				return False
			else:
				return True
		return False

	def LocalFileSelected(self, event):
		if not self.MutlipleLocalFilesSelected():
			filePath = self.path + '/' +  event.GetText()
			# print "File: ", filePath

			imagePath = filePath

			if filePath.endswith((SUPPORTED_VIDEO_EXTENSIONS)):
				imagePath = 'img/video.png'
			elif os.path.isdir(filePath):
				imagePath = 'img/preview.png'

			self.SetPreviewImage(imagePath)

	def LocalFileRightClicked(self, event):
		global HOST_SYS
		file = event.GetText()
		menu = wx.Menu()
		if file == '..' or os.path.isdir(self.path + '/' + file):
			item = menu.Append(wx.NewId(), "Open")
			self.Bind(wx.EVT_MENU, self.ShowSelectedDirectory, item)
		else:
			item = menu.Append(wx.NewId(), "Send to Player")
			self.Bind(wx.EVT_MENU, self.SendSelectedFilesToPlayer, item)
		rect = self.localList.GetRect()
		point = event.GetPoint()
		if HOST_SYS == HOST_WIN:
			self.PopupMenu(menu, (rect[0]+point[0]+10,rect[1]+point[1]+10))
		else:
			self.PopupMenu(menu, (rect[0]+point[0]+10,rect[1]+point[1]+30))
		menu.Destroy()

	def ShowSelectedDirectory(self, event):
		folder = self.localList.GetItemText(self.localList.GetFocusedItem())
		if folder == '..':
			self.ShowParentDirectory()
		else:
			newPath = self.path + '/' + folder
			self.ShowDirectory(newPath)

	def RemoteFileRightClicked(self, event):
		file = event.GetText()
		menu = wx.Menu()
		item = menu.Append(wx.NewId(), "Delete")
		self.Bind(wx.EVT_MENU, self.DeleteSelectedRemoteFile, item)
		rect = self.remoteList.GetRect()
		point = event.GetPoint()
		if HOST_SYS == HOST_WIN:
			self.PopupMenu(menu, (rect[0]+point[0]+10,rect[1]+point[1]+10))
		else:
			self.PopupMenu(menu, (rect[0]+point[0]+10,rect[1]+point[1]+30))
		menu.Destroy()

	def DeleteSelectedRemoteFile(self, event):
		index = self.remoteList.GetFirstSelected()
		files = []
		while not index == -1:
			item = self.remoteList.GetItem(index,0)
			fileName = item.GetText()
			files.append(str(fileName))
			index = self.remoteList.GetNextSelected(index)
		print "Files to delete: ", files
		self.DeleteRemoteFiles(files)


	def SendSelectedFilesToPlayer(self, event=None):
		index = self.localList.GetFirstSelected()
		files = []
		while not index == -1:
			item = self.localList.GetItem(index,0)
			fileName = item.GetText()
			files.append(fileName)
			index = self.localList.GetNextSelected(index)
		print "Files to send: ", files

		# optimize the files before sending them
		# create temp directory
		tmpPath = BASE_PATH + '/' + 'tmp'
		try:
			os.makedirs(tmpPath)
		except OSError as exception:
			print "Exception in creating DIR: ",exception
		rmutil.ImageUtil.OptimizeImages(files, self.path, tmpPath,1920,1080,HOST_SYS == HOST_WIN)
		network.tcpfileclient.sendFiles(files, tmpPath, self.host, self, HOST_SYS == HOST_WIN)
		print "Deleting temporary files..."
		shutil.rmtree(tmpPath)
		self.LoadRemoteFileList()

	def SetPreviewImage(self, imagePath):
		self._SetPreview('img/clear.png')
		self._SetPreview(imagePath)

	def _SetPreview(self, imagePath):
		#print "PREVIEW IMAGE PATH: " + imagePath
		path = resource_path(imagePath)
		#print "RESOURCE PATH: " + path
		img = wx.Image(path)
		# scale the image, preserving the aspect ratio
		W = img.GetWidth()
		H = img.GetHeight()

		maxSize = 200

		if W > H:
			NewW = maxSize
			NewH = maxSize * H / W
		else:
			NewH = maxSize
			NewW = maxSize * W / H
		img = img.Scale(NewW,NewH)

		self.imageCtrl.SetBitmap(wx.BitmapFromImage(img))

	def LocalFileDoubleClicked(self, event):
		fileName = event.GetText()
		filePath = self.path + '/' +  fileName
		# print "File: ", filePath
		if event.GetText() == '..':
			# directory up
			self.ShowParentDirectory()
		elif os.path.isdir(filePath):
			# open directory
			self.ShowDirectory(filePath)
		else:
			# dialog to verify sending file to player
			msg = "Send file '" + fileName + "' to the player? Stop and restart player when the process is complete!"
			dlg = wx.MessageDialog(self, msg, "Send file to Player", wx.YES_NO | wx.ICON_QUESTION)
			if dlg.ShowModal() == wx.ID_YES:
				self.SendSelectedFilesToPlayer()
			if HOST_SYS == HOST_WIN:
				dlg.Destroy()


	def RemoteFileDoubleClicked(self, event):
		fileName = event.GetText()
		self.DeleteRemoteFile(fileName)

	def DeleteRemoteFile(self, fileName):
		files = [str(fileName)]
		self.DeleteRemoteFiles(files)

	def DeleteRemoteFiles(self, files):
		# dialog to verify deleting file on player
		msg = "Delete the selected file(s) from the player (will stop and restart player)? This can not be undone!"
		dlg = wx.MessageDialog(self, msg, "Delete file(s) from player?", wx.YES_NO | wx.ICON_EXCLAMATION)
		if dlg.ShowModal() == wx.ID_YES:
			dlgStyle =  wx.PD_SMOOTH
			prgDialog = wx.ProgressDialog("Deleting file(s)...", "Deleting file(s) from player...", parent = self, style = dlgStyle)
			prgDialog.Pulse()
			args = ["-i", str(len(files))]
			for file in files:
				args.append("-s")
				args.append(file)
			msgData = network.messages.getMessage(DELETE_FILE, args)
			network.udpconnector.sendMessage(msgData, self.host)
			time.sleep(2)
			wx.CallAfter(prgDialog.Destroy)
			print "Delete timeout passed, initiating data load..."
			self.LoadData()
			#self.LoadRemoteFileList()

	def CheckboxToggled(self, event):
		checkbox = event.GetEventObject()
		print checkbox.GetName()
		msgData = network.messages.getConfigUpdateMessage(checkbox.GetName(), checkbox.IsChecked())
		network.udpconnector.sendMessage(msgData, self.host)

	def ChangeDir(self, event):
		dlg = wx.DirDialog(self, message="Select a directory that contains images or videos you would like to browse and upload to your media player.", defaultPath=self.path, style=wx.DD_CHANGE_DIR)

		# Call the dialog as a model-dialog so we're required to choose Ok or Cancel
		if dlg.ShowModal() == wx.ID_OK:
			# User has selected something, get the path
			filename = dlg.GetPath()
			print "Changing local list to new path: " + filename
			self.ShowDirectory(filename)
		dlg.Destroy()

	def ShowDirectory(self, newPath):
		if not self.path == newPath:
			self.path = newPath
			self.SetPreviewImage('img/preview.png')
			self.UpdateLocalFiles()

	def ShowParentDirectory(self, event=None):
		parent = os.path.abspath(os.path.join(self.path, os.pardir))
		self.ShowDirectory(parent)

	def LoadRemoteFileList(self, event=None):
		if not self.pageDataLoading:
			Publisher.subscribe(self.InsertReceivedFileList, 'remote_files')
			Publisher.subscribe(self.UdpListenerStopped, 'listener_stop')
		#network.udpresponselistener.registerObserver([OBS_FILE_LIST, self.InsertReceivedFileList])
		#network.udpresponselistener.registerObserver([OBS_STOP, self.UdpListenerStopped])
		msgData = network.messages.getMessage(FILELIST_REQUEST)
		dlgStyle =  wx.PD_AUTO_HIDE
		#self.prgDialog = wx.ProgressDialog("Loading...", "Loading filelist from player...", maximum = 1, parent = self.parent, style = dlgStyle)
		#self.prgDialog.Pulse()
		self.remoteListLoading = True
		#self.parent.prgDialog.Pulse("Loading filelist...")
		network.udpconnector.sendMessage(msgData, self.host)

	def LoadRemoteConfig(self, event=None):
		print "Entering LoadRemoteConfig routine...."
		if not self.pageDataLoading:
			Publisher.subscribe(self.UpdateConfigUI, 'config')
			Publisher.subscribe(self.UdpListenerStopped, 'listener_stop')
		#network.udpresponselistener.registerObserver([OBS_CONFIG, self.UpdateConfigUI])
		#network.udpresponselistener.registerObserver([OBS_STOP, self.UdpListenerStopped])
		print "Observers registered..."
		msgData = network.messages.getMessage(CONFIG_REQUEST)
		dlgStyle =  wx.PD_AUTO_HIDE
		#self.prgDialog = wx.ProgressDialog("Loading...", "Loading configuration from player...", maximum = 0, parent = self, style = dlgStyle)
		#self.prgDialog.Pulse()
		self.remoteListLoading = False
		#self.parent.prgDialog.Pulse("Loading configuration...")
		network.udpconnector.sendMessage(msgData, self.host)

	def UdpListenerStopped(self):
		print "UDP LISTENER STOPPED IN PANEL %d" % self.index
		global HOST_SYS
		if self.pageDataLoading:
			if self.remoteListLoading:
				self.pageDataLoading = False
				Publisher.unsubAll()
				if self.parent.prgDialog:
					print "CLOSING PRG DIALOG IN PARENT..."
					self.parent.prgDialog.Update(100)
					if HOST_SYS == HOST_WIN:
						self.parent.prgDialog.Destroy()
				if self.prgDialog:
					print "CLOSING PRG DIALOG IN PANEL..."
					self.prgDialog.Update(100)
					if HOST_SYS == HOST_WIN:
						self.prgDialog.Destroy()
			else:
				self.LoadRemoteFileList()
		else:
			if self.prgDialog:
				self.prgDialog.Update(100)
				if HOST_SYS == HOST_WIN:
					self.prgDialog.Destroy()

	def ButtonClicked(self, event):
		button = event.GetEventObject()
		if button.GetName() == 'btn_identify':
			msgData = network.messages.getMessage(PLAYER_IDENTIFY)
			network.udpconnector.sendMessage(msgData, self.host)
			msg = "The current player will show a test image. Close this dialog to exit identifier mode."
			dlg = wx.MessageDialog(self, msg, "Identifying player", wx.OK | wx.ICON_EXCLAMATION)
			if dlg.ShowModal() == wx.ID_OK:
				msgData2 = network.messages.getMessage(PLAYER_IDENTIFY_DONE)
				network.udpconnector.sendMessage(msgData2, self.host)
			dlg.Destroy()
		elif button.GetName() == 'btn_reboot':
			self.RebootPlayer()
		
	def RebootPlayer(self):
		self.prgDialog = wx.ProgressDialog("Rebooting...", wordwrap("Player rebooting, this can take up to 1 minute. This dialog will close when the reboot is complete, you may close it manually if you see your player up and running again.", 350, wx.ClientDC(self)), parent = self)
		# register observer
		# network.udpresponselistener.registerObserver([OBS_BOOT_COMPLETE, self.RebootComplete])
		# network.udpresponselistener.registerObserver([OBS_STOP, self.UdpListenerStopped])

		Publisher.subscribe(self.RebootComplete, "boot_complete")
		#Publisher.subscribe(self.UdpListenerStopped, 'listener_stop')
		self.prgDialog.Pulse()

		msgData = network.messages.getMessage(PLAYER_REBOOT)
		network.udpconnector.sendMessage(msgData, self.host, UDP_REBOOT_TIMEOUT)

	def RebootComplete(self):
		print "REBOOT COMPLETE CALLBACK"
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

# MAIN ROUTINE
if __name__ == '__main__':
	# set working directory to scripts path
	abspath = os.path.abspath(__file__)
	dname = os.path.dirname(abspath)
	os.chdir(dname)
	BASE_PATH = dname
	app = wx.App()

	# check platform
	if platform.system() == 'Windows':
		HOST_SYS = HOST_WIN
	elif platform.system() == 'Darwin':
		HOST_SYS = HOST_MAC
	elif platform.system() == 'Linux':
		HOST_SYS = HOST_LINUX

	frame = AppFrame(None, -1, 'RaspMedia Control')

	app.MainLoop()
