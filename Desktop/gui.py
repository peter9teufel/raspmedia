import Tkinter

class SimpleApp(Tkinter.Tk):
	def __init__(self,parent):
		Tkinter.Tk.__init__(self,parent)
		self.parent = parent
		self.initialize()


	def initialize(self):
		self.grid()
		# Text Entry
		self.entry_txt = Tkinter.StringVar()
		self.entry_txt.set("Enter text here...")
		self.entry = Tkinter.Entry(self, textvariable=self.entry_txt)
		self.entry.grid(column=0, row=0, sticky='EW')
		self.entry.bind("<Return>", self.onPressEnter)
		# Button
		button = Tkinter.Button(self, text=u"Click me!", command=self.onButtonClicked)
		button.grid(column=1, row=0)
		# Label
		self.label_txt = Tkinter.StringVar()
		label = Tkinter.Label(self, textvariable=self.label_txt, anchor='w', fg='white', bg='blue')
		label.grid(column=0, row=1, columnspan=2, sticky='EW')

		# set first column to resize
		self.grid_columnconfigure(0,weight=1)
		# disable vertical resizing
		self.resizable(True,False)
		self.update()
		self.geometry(self.geometry())

		# set focus on text field
		self.entry.focus_set()
		self.entry.selection_range(0, Tkinter.END)


	def onButtonClicked(self):
		self.label_txt.set(self.entry_txt.get())
		# set focus on text field
		self.entry.focus_set()
		self.entry.selection_range(0, Tkinter.END)

	def onPressEnter(self, event):
		self.label_txt.set(self.entry_txt.get())
		# set focus on text field
		self.entry.focus_set()
		self.entry.selection_range(0, Tkinter.END)

# MAIN ROUTINE
if __name__ == '__main__':
	app = SimpleApp(None)
	app.title('Media Control')
	app.mainloop()