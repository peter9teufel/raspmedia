import packages.rmnetwork as network
from packages.rmnetwork.constants import *
import os, sys, platform, ast, time, threading
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
# HOST SEARCH FRAME FOR WIN VERSION ############################################
################################################################################
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

		self.hostList.InsertColumn(0,"Host Address", width = 150)
		self.hostList.InsertColumn(1,"Player Name", width = 150)
		self.mainSizer.Add(self.hostList, (2,0))
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.HostListDoubleClicked, self.hostList)

		self.SetSizerAndFit(self.mainSizer)
		self.Center()
		self.Show(True)

	def HostFound(self, host, name):
		# self.hosts.Add(host)
		idx = self.hostList.InsertStringItem(0, host[0])

		port = str(host[1])
		print "Host insert in row " + str(idx) + ": " + host[0] + " - " + port
		self.hostList.SetStringItem(idx, 1, name)

	def searchHosts(self):
		# clear host list
		self.hostList.DeleteAllItems()
		network.udpresponselistener.registerObserver([OBS_HOST_SEARCH, self.HostFound])
		network.udpresponselistener.registerObserver([OBS_STOP, self.UdpListenerStopped])
		msgData = network.messages.getMessage(SERVER_REQUEST)
		self.prgDialog = wx.ProgressDialog("Searching...", "Searching available RaspMedia Players...")
		self.prgDialog.Pulse()
		network.udpconnector.sendMessage(msgData)

	def UdpListenerStopped(self):
		if self.prgDialog:
			self.prgDialog.Destroy()
		self.Raise()

	def HostListDoubleClicked(self, event):
		print "You double clicked ", event.GetText()
		playerName = self.hostList.GetItem(self.hostList.GetFirstSelected(),1).GetText()
		self.Hide()
		self.mediaCtrlFrame = RemoteFrame(self.parent,-1, playerName,event.GetText())
		#self.mediaCtrlFrame.SetHost(event.GetText())
		self.mediaCtrlFrame.Bind(wx.EVT_CLOSE, self.ChildFrameClosed)
		self.mediaCtrlFrame.Center()
		self.mediaCtrlFrame.Show(True)
		self.mediaCtrlFrame.Load()
		#self.mediaCtrlFrame.LoadRemoteConfig(None)
		#self.mediaCtrlFrame.LoadRemoteFileList(None)

	def ChildFrameClosed(self, event):
		self.mediaCtrlFrame.Destroy()
		self.Center()
		self.Show(True)
		self.searchHosts()

################################################################################
# REMOTE FRAME OF APP FOR WIN VERSION ##########################################
################################################################################

class RemoteFrame(wx.Frame):
	def __init__(self,parent,id,title,host):
		wx.Frame.__init__(self,parent,id,title,size=(600,600))
		self.parent = parent
		self.panel = RaspMediaCtrlPanel(self,-1,"RaspMedia Remote",0,host)
		self.prgDialog = None
		self.Center()
		self.Fit()

	def SetHost(self, host):
		self.panel.SetHost(host)

	def Load(self):
		self.panel.LoadRemoteConfig()
		self.SetSize((self.GetSize()[0]-1, self.GetSize()[1]-1))


################################################################################
# MAIN FRAME OF APP MAC AND LINUX ##############################################
################################################################################
class AppFrame(wx.Frame):
	def __init__(self,parent,id,title):
		wx.Frame.__init__(self,parent,id,title,size=(600,600))
		global playerCount
		self.parent = parent
		self.Bind(wx.EVT_CLOSE, self.Close)
		print "Initializing Notebook..."
		self.notebook = RemoteNotebook(self,-1,None)
		print "Showing window..."
		self.Show()
		retry = True
		while retry:
			print "Starting host search..."
			self.notebook.SearchHosts()
			print "Centering AppFrame and checking result..."
			self.Center()
			if playerCount == 0:
				self.notebook.prgDialog.Destroy()
				dlg = wx.MessageDialog(self,"No RaspMedia Players found, check if your players are running and connected to the local network, restart the application to try again.", "No Player found", style = wx.OK)
				if dlg.ShowModal() == wx.ID_OK:
					self.Close()
			else:
				retry = False
				self.notebook.prgDialog.Raise()
				self.notebook.LoadPageData(0)
		self.SetSize((self.GetSize()[0]-53, self.GetSize()[1]))

	def Close(self, event=None):
		global playerCount
		playerCount = 0
		self.notebook.Close()
		self.Destroy()
		sys.exit(0)

	def SetupMenuBar(self):
		# menus
		fileMenu = wx.Menu()
		helpMenu = wx.Menu()

		# File Menu
		menuExit = fileMenu.Append(wx.ID_EXIT, "&Exit RaspMedia Control"," Terminate the program")
		self.Bind(wx.EVT_MENU, self.Close, menuExit)

		# Help Menu
		about = helpMenu.Append(wx.ID_ANY, "&About")

		# Menubar
		menuBar = wx.MenuBar()
		menuBar.Append(fileMenu,"&File") # Adding the "filemenu" to the MenuBar
		menuBar.Append(helpMenu, "&Help")
		self.SetMenuBar(menuBar)

################################################################################
# REMOTE NOTEBOOK FOR PLAYER PANELS MAC AND LINUX ##############################
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
		global HOST_SYS
		if HOST_SYS == HOST_LINUX:
			self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
		elif HOST_SYS == HOST_MAC:
			self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanged)

	def Close(self):
		self.Destroy()

	def HostFound(self, host, playerName):
		global playerCount
		print "HOST FOUND!"
		# add page for found Player
		page = RaspMediaCtrlPanel(self,-1,playerName,playerCount,host[0])
		page.SetHost(host[0])
		self.pages.append(page)
		#page.LoadRemoteConfig()
		#page.LoadRemoteFileList()
		#page.Fit()
		self.AddPage(page, playerName)
		playerCount += 1
		self.Fit()
		self.parent.Fit()
		# self.hosts.Add(host)
		#idx = self.hostList.InsertStringItem(0, playerName)
		#port = str(host[1])
		#print "Host insert in row " + str(idx) + ": " + host[0] + " - " + port
		#self.hostList.SetStringItem(idx, 1, host[0])

	def SearchHosts(self):
		# clear host list
		#self.hostList.DeleteAllItems()
		network.udpresponselistener.registerObserver([OBS_HOST_SEARCH, self.HostFound])
		network.udpresponselistener.registerObserver([OBS_STOP, self.UdpListenerStopped, self])
		msgData = network.messages.getMessage(SERVER_REQUEST)
		self.prgDialog = wx.ProgressDialog("Searching...", "Searching available RaspMedia Players...")
		self.prgDialog.Pulse()
		#self.prgDialog.SetFocus()
		self.prgDialog.Raise()
		network.udpconnector.sendMessage(msgData)

	def LoadPageData(self, pageNumber):
		print "Loading config and remote list for page ", pageNumber
		self.GetPage(pageNumber).pageDataLoading = True
		self.GetPage(pageNumber).LoadRemoteConfig()
		#self.GetPage(pageNumber).LoadRemoteFileList()

	def UdpListenerStopped(self):
		global playerCount
		network.udpresponselistener.removeObserver([OBS_HOST_SEARCH, self.HostFound])
		network.udpresponselistener.removeObserver([OBS_STOP, self.UdpListenerStopped])
		print "Number of observers: ", len(network.udpresponselistener.observers)
		print "Number of players found: ", playerCount
		self.Update()

	def OnPageChanged(self, event):
		global HOST_SYS
		print "ON PAGE CHANGED TRIGGER"
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
			dlg = wx.ProgressDialog("Loading...", "Loading Player Data...")
			dlg.Pulse()
			self.LoadRemoteConfig()
			time.sleep(0.5)
			dlg.Destroy()

	def Initialize(self):
		self.SetupFileLists()
		self.SetupPlayerSection()
		self.SetupConfigSection()

		self.mainSizer.Add(self.playerSizer,(0,0), flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, border=10)
		self.mainSizer.Add(self.configSizer, (0,2), flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, border=10)

		self.mainSizer.Add(self.filesSizer, (2,0), span=(1,4), flag=wx.BOTTOM | wx.LEFT | wx.RIGHT, border=10)

		self.SetSizerAndFit(self.mainSizer)

		line = wx.StaticLine(self,-1,size=(self.mainSizer.GetSize()[0],2))
		self.mainSizer.Add(line, (1,0), span=(1,4))

		line = wx.StaticLine(self,-1,size=(2,self.mainSizer.GetCellSize(0,0)[1]),style=wx.LI_VERTICAL)
		self.mainSizer.Add(line,(0,1), flag = wx.LEFT, border = 10)
		# self.SetSizeHints(self.GetSize().x,self.GetSize().y,-1,self.GetSize().y)
		#self.SetSizerAndFit(self.mainSizer)
		self.Show(True)

	def SetupPlayerSection(self):
		# Text label
		label = wx.StaticText(self,-1,label="Remote Control:")
		self.playerSizer.Add(label,(0,0),(1,2), flag = wx.BOTTOM, border=5)

		# Play and Stop Button
		button = wx.Button(self,-1,label="Play")
		self.playerSizer.Add(button,(1,0))
		self.Bind(wx.EVT_BUTTON, self.PlayClicked, button)

		button = wx.Button(self,-1,label="Stop")
		self.playerSizer.Add(button,(2,0), flag=wx.TOP, border=5)
		self.Bind(wx.EVT_BUTTON, self.StopClicked, button)

		line = wx.StaticLine(self,-1,size=(button.GetSize()[0],2))
		self.playerSizer.Add(line,(3,0), flag=wx.TOP | wx.BOTTOM, border=10)

		button = wx.Button(self,-1,label="Identify")
		button.SetName("btn_identify")
		self.playerSizer.Add(button,(4,0))
		self.Bind(wx.EVT_BUTTON, self.ButtonClicked, button)

		button = wx.Button(self,-1,label="Reboot")
		button.SetName("btn_reboot")
		self.playerSizer.Add(button,(5,0), flag=wx.TOP, border=5)
		self.Bind(wx.EVT_BUTTON, self.ButtonClicked, button)

	def SetupConfigSection(self):
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

		# Sample code for bitmap button
		#imageFile = "img/ic_edit.png"
		#editIcon = wx.Image(imageFile, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
		#self.editInterval = wx.BitmapButton(self, id=-1, bitmap=editIcon, size = (editIcon.GetWidth()+10, editIcon.GetHeight()+10))
		#self.editName = wx.BitmapButton(self, id=-1, bitmap=editIcon, size = (editIcon.GetWidth()+10, editIcon.GetHeight()+10))

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

		self.configSizer.Add(wx.StaticText(self,-1,label="Configuration:"),(0,0), flag=wx.BOTTOM, border=5)
		self.configSizer.Add(self.cbImgEnabled, (1,0))
		self.configSizer.Add(self.cbVidEnabled, (2,0))
		self.configSizer.Add(self.cbAutoplay, (1,1))
		self.configSizer.Add(self.cbRepeat, (2,1))
		self.configSizer.Add(intervalLabel, (4,0), flag=wx.ALIGN_CENTER_VERTICAL)
		self.configSizer.Add(self.imgIntervalLabel, (4,1), flag=wx.ALIGN_CENTER_VERTICAL)
		self.configSizer.Add(self.editInterval, (4,3))
		self.configSizer.Add(nameLabel, (5,0), flag=wx.ALIGN_CENTER_VERTICAL)
		self.configSizer.Add(self.playerNameLabel, (5,1), flag=wx.ALIGN_CENTER_VERTICAL)
		self.configSizer.Add(self.editName, (5,3))
		self.configSizer.Add(addrLabel, (6,0), flag = wx.ALIGN_CENTER_VERTICAL)
		self.configSizer.Add(playerAddr, (6,1), flag = wx.ALIGN_CENTER_VERTICAL)
		self.configSizer.Add(updateBtn, (0,4))
		self.configSizer.Add(line, (3,0), span=(1,5), flag=wx.TOP | wx.BOTTOM, border=5)

	def SetupFileLists(self):
		self.filesSizer.SetEmptyCellSize((0,0))
		# setup file lists and image preview
		self.AddLocalList()
		self.AddImagePreview()
		self.AddRemoteList()

		imageFile = resource_path("img/ic_folder_select.png")
		btnIcon = wx.Image(imageFile, wx.BITMAP_TYPE_ANY)
		btnIcon = btnIcon.Scale(30,30)
		btnIcon = btnIcon.ConvertToBitmap()
		selectFolder = wx.BitmapButton(self, id=-1, bitmap=btnIcon, pos=(7,7), size=(44,44))
		self.filesSizer.Add(selectFolder, (0,0))
		self.Bind(wx.EVT_BUTTON, self.ChangeDir, selectFolder)

		#separator = wx.StaticLine(self,-1,size=(2,35), style=wx.LI_VERTICAL)
		#self.filesSizer.Add(separator, (0,1), flag = wx.ALIGN_CENTER)

		#button = wx.Button(self,-1,label="Change local directory")
		#self.filesSizer.Add(button,(0,0))
		#self.Bind(wx.EVT_BUTTON, self.ChangeDir, button)

		#imageFile = "img/ic_folder_up.png"
		#btnIcon = wx.Image(imageFile, wx.BITMAP_TYPE_ANY)
		#btnIcon = btnIcon.Scale(30,30)
		#btnIcon = btnIcon.ConvertToBitmap()
		#folderUp = wx.BitmapButton(self, id=-1, bitmap=btnIcon, pos=(7,7), size=(44,44))
		#self.filesSizer.Add(folderUp, (0,2), flag = wx.ALIGN_RIGHT)
		#self.Bind(wx.EVT_BUTTON, self.ShowParentDirectory, folderUp)

		button = wx.Button(self,-1,label="Refresh remote filelist")
		self.filesSizer.Add(button,(3,0))
		self.Bind(wx.EVT_BUTTON, self.LoadRemoteFileList, button)
		self.filesSizer.Fit(self)

	def AddLocalList(self):
		id=wx.NewId()
		self.localList=wx.ListCtrl(self,id,size=(400,200),style=wx.LC_REPORT|wx.SUNKEN_BORDER)
		self.localList.Show(True)

		self.localList.InsertColumn(0,"Local Files: " + self.path, width = 598)
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
		id=wx.NewId()
		self.remoteList=wx.ListCtrl(self,id,size=(600,200),style=wx.LC_REPORT|wx.SUNKEN_BORDER)
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
					files.append(file)
				elif os.path.isdir(self.path + '/' + file):
					folders.append(file)

		for folderName in folders:
			self.localList.InsertStringItem(self.localList.GetItemCount(), folderName)

		for curFile in files:
			self.localList.InsertStringItem(self.localList.GetItemCount(), curFile)

		col = self.localList.GetColumn(0)
		col.SetText(self.path)
		self.localList.SetColumn(0, col)

	def InsertReceivedFileList(self, serverAddr, files):
		print "UPDATING REMOTE FILELIST UI..."
		self.remoteList.DeleteAllItems()
		files.sort()
		for file in reversed(files):
			if not file.startswith('.') and '.' in file:
				self.remoteList.InsertStringItem(0, file)

	def UpdateConfigUI(self, config):
		print "UPDATING CONFIG UI..."
		global HOST_SYS
		configDict = ast.literal_eval(config)
		print configDict
		self.cbImgEnabled.SetValue(configDict['image_enabled'])
		self.cbVidEnabled.SetValue(configDict['video_enabled'])
		self.cbRepeat.SetValue(configDict['repeat'])
		self.cbAutoplay.SetValue(configDict['autoplay'])
		self.imgIntervalLabel.SetLabel(str(configDict['image_interval']))
		self.playerNameLabel.SetLabel(str(configDict['player_name']))

		if HOST_SYS == HOST_MAC or HOST_SYS == HOST_LINUX:
			if self.notebook_event:
				self.parent.SetPageText(self.notebook_event.GetSelection(), str(configDict['player_name']))
			else:
				self.parent.SetPageText(self.parent.GetSelection(), str(configDict['player_name']))
			self.parent.parent.Refresh()
		elif HOST_SYS == HOST_WIN:
			self.parent.SetTitle(str(configDict['player_name']))

	def LocalFileSelected(self, event):
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


	def SendSelectedFilesToPlayer(self, event):
		index = self.localList.GetFirstSelected()
		files = []
		while not index == -1:
			item = self.localList.GetItem(index,0)
			fileName = item.GetText()
			files.append(fileName)
			index = self.localList.GetNextSelected(index)
		print "Files to send: ", files
		for file in files:
			self.SendFileToPlayer(file)
		self.LoadRemoteFileList()

	def SendFileToPlayer(self, fileName):
		filePath = self.path + '/' +  fileName
		print "Path: ", filePath
		network.tcpfileclient.registerObserver(self.LoadRemoteFileList)
		network.tcpfileclient.sendFile(filePath, self.host, self)

	def SetPreviewImage(self, imagePath):
		self._SetPreview('img/clear.png')
		self._SetPreview(imagePath)

	def _SetPreview(self, imagePath):
		print "PREVIEW IMAGE PATH: " + imagePath
		path = resource_path(imagePath)
		print "RESOURCE PATH: " + path
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
				network.tcpfileclient.registerObserver(self.LoadRemoteFileList)
				network.tcpfileclient.sendFile(filePath, self.host, self)
				self.LoadRemoteFileList()
			dlg.Destroy()


	def RemoteFileDoubleClicked(self, event):
		fileName = event.GetText()
		self.DeleteRemoteFile(fileName)

	def DeleteRemoteFile(self, fileName):
		files = [fileName]
		self.DeleteRemoteFiles(files)

	def DeleteRemoteFiles(self, files):
		# dialog to verify deleting file on player
		msg = "Delete the selected file(s) from the player (will stop and restart player)? This can not be undone!"
		dlg = wx.MessageDialog(self, msg, "Delete file(s) from player?", wx.YES_NO | wx.ICON_EXCLAMATION)
		if dlg.ShowModal() == wx.ID_YES:
			dlgStyle =  wx.PD_AUTO_HIDE
			self.prgDialog = wx.ProgressDialog("Deleting file(s)...", "Deleting file(s) from player...", maximum = 1, parent = self, style = dlgStyle)
			self.prgDialog.Pulse()
			args = ["-i", str(len(files))]
			for file in files:
				args.append("-s")
				args.append(file)
			msgData = network.messages.getMessage(DELETE_FILE, args)
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
		network.udpresponselistener.registerObserver([OBS_FILE_LIST, self.InsertReceivedFileList])
		network.udpresponselistener.registerObserver([OBS_STOP, self.UdpListenerStopped])
		msgData = network.messages.getMessage(FILELIST_REQUEST)
		dlgStyle =  wx.PD_AUTO_HIDE
		#self.prgDialog = wx.ProgressDialog("Loading...", "Loading filelist from player...", maximum = 1, parent = self.parent, style = dlgStyle)
		#self.prgDialog.Pulse()
		self.remoteListLoading = True
		#self.parent.prgDialog.Pulse("Loading filelist...")
		network.udpconnector.sendMessage(msgData, self.host)

	def LoadRemoteConfig(self, event=None):
		print "Entering LoadRemoteConfig routine...."
		network.udpresponselistener.registerObserver([OBS_CONFIG, self.UpdateConfigUI])
		network.udpresponselistener.registerObserver([OBS_STOP, self.UdpListenerStopped])
		print "Observers registered..."
		msgData = network.messages.getMessage(CONFIG_REQUEST)
		dlgStyle =  wx.PD_AUTO_HIDE
		#self.prgDialog = wx.ProgressDialog("Loading...", "Loading configuration from player...", maximum = 0, parent = self, style = dlgStyle)
		#self.prgDialog.Pulse()
		self.remoteListLoading = False
		#self.parent.prgDialog.Pulse("Loading configuration...")
		network.udpconnector.sendMessage(msgData, self.host)

	def UdpListenerStopped(self):
		global HOST_SYS
		if self.remoteListLoading:
			if HOST_SYS == HOST_MAC or HOST_SYS == HOST_LINUX:
				if self.parent.prgDialog:
					self.parent.prgDialog.Hide()
					self.parent.prgDialog.Destroy()
					self.parent.prgDialog = None
		else:
			self.LoadRemoteFileList()
		if self.prgDialog:
			self.prgDialog.Destroy()
			self.prgDialog = None

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
		elif button.GetName() == 'btn_image_interval':
			dlg = wx.TextEntryDialog(self, "New Interval:", "Image Interval", self.imgIntervalLabel.GetLabel())
			if dlg.ShowModal() == wx.ID_OK:
				try:
					newInterval = int(dlg.GetValue())
					self.imgIntervalLabel.SetLabel(str(newInterval))
					msgData = network.messages.getConfigUpdateMessage("image_interval", newInterval)
					network.udpconnector.sendMessage(msgData, self.host)
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
				dlg = wx.ProgressDialog("Updating", "Updating player name...")
				dlg.Pulse()
				self.LoadRemoteConfig()
				time.sleep(0.5)
				dlg.Destroy()
			dlg.Destroy()
		elif button.GetName() == 'btn_reboot':
			self.RebootPlayer()
		elif button.GetName() == 'btn_update':
			# register observer
			network.udpresponselistener.registerObserver([OBS_UPDATE, self.OnPlayerUpdated])
			network.udpresponselistener.registerObserver([OBS_STOP, self.UdpListenerStopped])

			self.prgDialog = wx.ProgressDialog("Updating...", "Player is trying to update, please stand by...")
			#self.prgDialog.ShowModal()
			self.prgDialog.Pulse()

			msgData = network.messages.getMessage(PLAYER_UPDATE)
			network.udpconnector.sendMessage(msgData, self.host, UDP_UPDATE_TIMEOUT)

	def RebootPlayer(self):
		network.udpresponselistener.registerObserver([OBS_BOOT_COMPLETE, self.RebootComplete])
		network.udpresponselistener.registerObserver([OBS_STOP, self.UdpListenerStopped])

		waitingTime = UDP_REBOOT_TIMEOUT
		self.prgDialog = wx.ProgressDialog("Rebooting...", "The player is rebooting, this can take up to 1 minute - please stand by...")
		self.prgDialog.Pulse()

		msgData = network.messages.getMessage(PLAYER_REBOOT)
		network.udpconnector.sendMessage(msgData, self.host, UDP_REBOOT_TIMEOUT)

	def RebootComplete(self):
		self.prgDialog.Destroy()
		dlg = wx.MessageDialog(self,"Reboot complete!","",style=wx.OK)
		dlg.Show()

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
		print "BASE PATH FOUND: "+ base_path
	except Exception:
		print "BASE PATH NOT FOUND!"
		base_path = BASE_PATH
	print "JOINING " + base_path + " WITH " + relative_path
	resPath = os.path.normcase(os.path.join(base_path, relative_path))
	#resPath = base_path + relative_path
	print resPath
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
		frame = ConnectFrame(None, -1, 'RaspMedia Control')
	elif platform.system() == 'Darwin':
		HOST_SYS = HOST_MAC
		frame = AppFrame(None, -1, 'RaspMedia Control')
	elif platform.system() == 'Linux':
		HOST_SYS = HOST_LINUX
		frame = AppFrame(None, -1, 'RaspMedia Control')

	app.MainLoop()
