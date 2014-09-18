from packages.rmgui import ImageTransferFrame as rm_app
from packages.rmnetwork.constants import *
import os, platform, shutil
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

from os.path import expanduser
home = expanduser("~")
appPath = home + '/.raspmedia/'
tmpPath = appPath + 'tmp/'
if not os.path.isdir(appPath):
    os.mkdir(appPath)

if os.path.isdir(tmpPath):
    shutil.rmtree(tmpPath)
os.mkdir(tmpPath)

frame = rm_app.ImageTransferFrame(None, -1, 'RaspMedia Image Transfer', base_path)

app.MainLoop()
