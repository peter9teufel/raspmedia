import packages.rmnetwork as network
from packages.rmnetwork.constants import *
import os, sys, ast, time
try:
	import wx
except ImportError:
	raise ImportError,"Wx Python is required."

################################################################################
# MAIN FRAME OF APP ############################################################
################################################################################
class AppFrame(wx.Frame):
	def __init__(self,parent,id,title):
		wx.Frame.__init__(self,parent,id,title,size=(600,600))
		self.parent = parent
		self.Bind(wx.EVT_CLOSE, self.Close)
		self.notebook = RemoteNotebook(self,-1,None)
		self.Center()
		self.Show()
		self.notebook.LoadPageData(0)

	def Close(self, event):
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
		self.SearchHosts()
		time.sleep(1)
		self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
		self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)

	def Close(self):
		self.Destroy()

	def HostFound(self, host, playerName):
		# add page for found Player
		page = RaspMediaCtrlPanel(self,-1,playerName)
		page.SetHost(host[0])
		#page.LoadRemoteConfig()
		#page.LoadRemoteFileList()
		#page.Fit()
		self.AddPage(page, playerName)
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
		network.udpresponselistener.registerObserver([OBS_STOP, self.UdpListenerStopped])
		msgData = network.messages.getMessage(SERVER_REQUEST)
		dlgStyle =  wx.PD_AUTO_HIDE
		self.prgDialog = wx.ProgressDialog("Searching...", "Searching available RaspMedia Players...", maximum = 1, parent = self, style = dlgStyle)
		self.prgDialog.Pulse()
		network.udpconnector.sendMessage(msgData)

	def LoadPageData(self, pageNumber):
		print "Loading config and remote list for page ", pageNumber
		self.GetPage(pageNumber).LoadRemoteConfig()
		self.GetPage(pageNumber).LoadRemoteFileList()

	def UdpListenerStopped(self):
		if self.prgDialog:
			self.prgDialog.Update(1)
			self.prgDialog.Destroy()
		network.udpresponselistener.removeObserver([OBS_HOST_SEARCH, self.HostFound])
		network.udpresponselistener.removeObserver([OBS_STOP, self.UdpListenerStopped])
		self.Update()

	def OnPageChanged(self, event):
		old = event.GetOldSelection()
		new = event.GetSelection()
		sel = self.GetSelection()
		self.LoadPageData(sel)
		self.log.write('OnPageChanged,  old:%d, new:%d, sel:%d\n' % (old, new, sel))
		event.Skip()

	def OnPageChanging(self, event):
		old = event.GetOldSelection()
		new = event.GetSelection()
		sel = self.GetSelection()
		self.LoadPageData(sel)
		self.log.write('OnPageChanging, old:%d, new:%d, sel:%d\n' % (old, new, sel))
		event.Skip()


################################################################################
# RASP MEDIA CONTROL PANEL #####################################################
################################################################################
class RaspMediaCtrlPanel(wx.Panel):
	def __init__(self,parent,id,title):
		#wx.Panel.__init__(self,parent,id,title)
		wx.Panel.__init__(self,parent,-1)
		self.parent = parent
		self.path = self.DefaultPath()
		self.mainSizer = wx.GridBagSizer()
		self.configSizer = wx.GridBagSizer()
		self.playerSizer = wx.GridBagSizer()
		self.filesSizer = wx.GridBagSizer()
		self.prgDialog = None
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

	def Initialize(self):
		self.SetupFileLists()
		self.SetupPlayerSection()
		self.SetupConfigSection()

		self.mainSizer.Add(self.playerSizer,(0,0), flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, border=10)
		self.mainSizer.Add(self.configSizer, (0,2), flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, border=10)

		self.mainSizer.Add(self.filesSizer, (2,0), span=(1,4), flag=wx.ALL, border=10)


		self.SetSizerAndFit(self.mainSizer)

		line = wx.StaticLine(self,-1,size=(self.mainSizer.GetSize()[0],2))
		self.mainSizer.Add(line, (1,0), span=(1,4))

		line = wx.StaticLine(self,-1,size=(2,self.mainSizer.GetCellSize(0,0)[1]),style=wx.LI_VERTICAL)
		self.mainSizer.Add(line,(0,1), flag = wx.LEFT, border = 10)

		# self.SetSizeHints(self.GetSize().x,self.GetSize().y,-1,self.GetSize().y)
		self.Show(True)

	def SetupPlayerSection(self):
		# Text label
		label = wx.StaticText(self,-1,label="Remote Control:")
		self.playerSizer.Add(label,(0,0),(1,2), flag = wx.EXPAND | wx.BOTTOM, border=5)

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

	def SetupConfigSection(self):
		# checkboxes
		self.cbImgEnabled = wx.CheckBox(self, -1, "Enable Images")
		self.cbVidEnabled = wx.CheckBox(self, -1, "Enable Videos")
		self.cbAutoplay = wx.CheckBox(self, -1, "Autoplay")
		self.cbRepeat = wx.CheckBox(self, -1, "Repeat")

		# interval and player name
		intervalLabel = wx.StaticText(self,-1,label="Image interval:")
		self.imgIntervalLabel = wx.StaticText(self,-1,label="")
		nameLabel = wx.StaticText(self,-1,label="Player name:")
		self.playerNameLabel = wx.StaticText(self,-1,label="")

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

		# bind UI element events
		self.Bind(wx.EVT_CHECKBOX, self.CheckboxToggled, self.cbImgEnabled)
		self.Bind(wx.EVT_CHECKBOX, self.CheckboxToggled, self.cbVidEnabled)
		self.Bind(wx.EVT_CHECKBOX, self.CheckboxToggled, self.cbAutoplay)
		self.Bind(wx.EVT_CHECKBOX, self.CheckboxToggled, self.cbRepeat)
		self.Bind(wx.EVT_BUTTON, self.ButtonClicked, self.editInterval)
		self.Bind(wx.EVT_BUTTON, self.ButtonClicked, self.editName)

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
		self.configSizer.Add(line, (3,0), span=(1,4), flag=wx.TOP | wx.BOTTOM, border=5)

	def SetupFileLists(self):
		self.filesSizer.SetEmptyCellSize((0,0))
		# setup file lists and image preview
		self.AddLocalList()
		self.AddImagePreview()
		self.AddRemoteList()

		imageFile = "img/ic_folder_select.png"
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
		self.UpdateLocalFiles()

	def AddImagePreview(self):
		img = wx.EmptyImage(200,200)
		self.imageCtrl = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(img))
		self.SetPreviewImage(os.getcwd() + '/img/preview.png')
		self.filesSizer.Add(self.imageCtrl, (1,1), flag = wx.LEFT, border=5)

	def AddRemoteList(self):
		id=wx.NewId()
		self.remoteList=wx.ListCtrl(self,id,size=(600,200),style=wx.LC_REPORT|wx.SUNKEN_BORDER)
		self.remoteList.Show(True)
		self.remoteList.InsertColumn(0,"Remote Files: ", width = 598)
		self.filesSizer.Add(self.remoteList, (2,0), span=(1,2), flag = wx.EXPAND | wx.TOP, border = 10)
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.RemoteFileDoubleClicked, self.remoteList)

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
		self.remoteList.DeleteAllItems()
		files.sort()
		for file in files:
			if not file.startswith('.') and '.' in file:
				self.remoteList.InsertStringItem(self.remoteList.GetItemCount(), file)

	def UpdateConfigUI(self, config):
		print "Update CONFIG METHOD"
		configDict = ast.literal_eval(config)
		print configDict
		self.cbImgEnabled.SetValue(configDict['image_enabled'])
		self.cbVidEnabled.SetValue(configDict['video_enabled'])
		self.cbRepeat.SetValue(configDict['repeat'])
		self.cbAutoplay.SetValue(configDict['autoplay'])
		self.imgIntervalLabel.SetLabel(str(configDict['image_interval']))
		self.playerNameLabel.SetLabel(str(configDict['player_name']))

	def LocalFileSelected(self, event):
		filePath = self.path + '/' +  event.GetText()
		# print "File: ", filePath

		imagePath = filePath

		if filePath.endswith((SUPPORTED_VIDEO_EXTENSIONS)):
			imagePath = os.getcwd() + '/img/video.png'
		elif os.path.isdir(filePath):
			imagePath = os.getcwd() + '/img/preview.png'

		self.SetPreviewImage(imagePath)


	def SetPreviewImage(self, imagePath):
		img = wx.Image(imagePath)
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
			pass
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
				self.LoadRemoteFileList(None)
			dlg.Destroy()


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
			self.ShowDirectory(filename)
		dlg.Destroy() # we don't need the dialog any more so we ask it to clean-up

	def ShowDirectory(self, newPath):
		if not self.path == newPath:
			self.path = newPath
			self.SetPreviewImage(os.getcwd() + '/img/preview.png')
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
		network.udpconnector.sendMessage(msgData, self.host)

	def LoadRemoteConfig(self, event=None):
		network.udpresponselistener.registerObserver([OBS_CONFIG, self.UpdateConfigUI])
		network.udpresponselistener.registerObserver([OBS_STOP, self.UdpListenerStopped])
		msgData = network.messages.getMessage(CONFIG_REQUEST)
		dlgStyle =  wx.PD_AUTO_HIDE
		#self.prgDialog = wx.ProgressDialog("Loading...", "Loading configuration from player...", maximum = 1, parent = self.parent, style = dlgStyle)
		#self.prgDialog.Pulse()
		network.udpconnector.sendMessage(msgData, self.host)

	def UdpListenerStopped(self):
		if self.prgDialog:
			self.prgDialog.Update(1)
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
		elif button.GetName() == 'btn_image_interval':
			dlg = wx.TextEntryDialog(self, "New Interval:", "Image Interval", self.imgIntervalLabel.GetLabel())
			if dlg.ShowModal() == wx.ID_OK:
				newInterval = int(dlg.GetValue())
				self.imgIntervalLabel.SetLabel(str(newInterval))
				msgData = network.messages.getConfigUpdateMessage("image_interval", newInterval)
				network.udpconnector.sendMessage(msgData, self.host)
				#except Exception, e:
				#	error = wx.MessageDialog(self, "Please enter a valid number!", "Invalid interval", wx.OK | wx.ICON_EXCLAMATION)
				#	error.ShowModal()

			dlg.Destroy()
		elif button.GetName() == 'btn_player_name':
			dlg = wx.TextEntryDialog(self, "New name:", "Player Name", self.playerNameLabel.GetLabel())
			if dlg.ShowModal() == wx.ID_OK:
				newName = dlg.GetValue()
				self.playerNameLabel.SetLabel(newName)
				msgData = network.messages.getConfigUpdateMessage("player_name", str(newName))
				network.udpconnector.sendMessage(msgData, self.host)
			dlg.Destroy()


	def PlayClicked(self, event):
		msgData = network.messages.getMessage(PLAYER_START)
		network.udpconnector.sendMessage(msgData, self.host)

	def StopClicked(self, event):
		msgData = network.messages.getMessage(PLAYER_STOP)
		network.udpconnector.sendMessage(msgData, self.host)


# MAIN ROUTINE
if __name__ == '__main__':
	# set working directory to scripts path
	abspath = os.path.abspath(__file__)
	dname = os.path.dirname(abspath)
	os.chdir(dname)
	app = wx.App()
	# frame = RaspMediaCtrlFrame(None, -1, 'RaspMedia Control')
	# frame = ConnectFrame(None, -1, 'RaspMedia Control')
	frame = AppFrame(None, -1, 'RaspMedia Control')
	app.MainLoop()
