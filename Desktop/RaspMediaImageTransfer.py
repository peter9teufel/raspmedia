from packages.rmgui import ImageTransferFrame as rm_app
from packages.rmnetwork.constants import *
import os, platform
try:
    import wx
except ImportError:
    raise ImportError,"Wx Python is required."


# set working directory to scripts path
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
base_path = dname
app = wx.App()

frame = rm_app.ImageTransferFrame(None, -1, 'RaspMedia Image Transfer', base_path)

app.MainLoop()
