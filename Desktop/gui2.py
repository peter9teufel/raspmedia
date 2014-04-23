try:
	import wx
except ImportError:
	raise ImportError,"Wx Python is required."

class SimpleApp(wx.Frame):
	def __init__(self,parent,id,title):
		wx.Frame.__init__(self,parent,id,title)
		self.parent = parent
		self.initialize()


	def initialize(self):
		sizer = wx.GridBagSizer()

		# Text Entry
		self.entry = wx.TextCtrl(self,-1,value=u"Enter text here...",style=wx.TE_PROCESS_ENTER)
		sizer.Add(self.entry,(0,0),(1,1),wx.EXPAND)
		self.Bind(wx.EVT_TEXT_ENTER, self.OnPressEnter, self.entry)

		# Button
		button = wx.Button(self,-1,label="Click me!")
		sizer.Add(button,(0,1))
		self.Bind(wx.EVT_BUTTON, self.OnButtonClicked, button)

		# Text label
		self.label = wx.StaticText(self,-1,label="Hello!")
		self.label.SetBackgroundColour(wx.BLUE)
		self.label.SetForegroundColour(wx.WHITE)
		sizer.Add(self.label,(1,0),(1,2),wx.EXPAND)

		sizer.AddGrowableCol(0)
		self.SetSizerAndFit(sizer)
		self.SetSizeHints(self.GetSize().x,self.GetSize().y,-1,self.GetSize().y)
		self.FocusTextEntry()
		self.Show(True)


	def OnButtonClicked(self, event):
		self.label.SetLabel(self.entry.GetValue())
		self.FocusTextEntry()

	def OnPressEnter(self, event):
		self.label.SetLabel(self.entry.GetValue())
		self.FocusTextEntry()

	def FocusTextEntry(self):
		self.entry.SetFocus()
		self.entry.SetSelection(-1,-1)

# MAIN ROUTINE
if __name__ == '__main__':
	app = wx.App()
	frame = SimpleApp(None, -1, 'Media Control')
	app.MainLoop()