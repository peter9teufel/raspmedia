from packages.rmgui import AppFrame as rm_app
from packages.rmnetwork.constants import *
import os, platform
try:
    import wx
except ImportError:
    raise ImportError,"Wx Python is required."


# MAIN ROUTINE
if __name__ == '__main__':
    # set working directory to scripts path
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)
    base_path = dname
    app = wx.App()

    frame = rm_app.AppFrame(None, -1, 'RaspMedia Control', base_path)

    app.MainLoop()
