import wx, os, platform, shutil
from PIL import Image
import wx.lib.scrolledpanel as scrolled
import sys
from packages.lang.Localizer import *

BASE_PATH = ""

################################################################################
# SCROLLABLE SELECTABLE IMAGE VIEW #############################################
################################################################################
class ScrollableSelectableImageView(scrolled.ScrolledPanel):
    def __init__(self,parent,id,size,images=[],cols=2,deletion=False,execPath=None):
        scrolled.ScrolledPanel.__init__(self,parent,id,size=size,style=wx.SUNKEN_BORDER)
        self.id = id
        self.parent = parent
        w = size[0] - 14
        self.size = (w,size[1])
        self.cols = cols
        self.deletion = deletion
        self.mainSizer = wx.GridBagSizer()
        abspath = os.path.abspath(__file__)
        self.dname = os.path.dirname(abspath)

        from os.path import expanduser
        home = expanduser("~")
        appPath = home + '/.raspmedia/'
        tmpPath = appPath + 'tmp/'
        if not os.path.isdir(appPath):
            os.mkdir(appPath)
        if not os.path.isdir(tmpPath):
            os.mkdir(tmpPath)
        self.tmpRoot = tmpPath

        # create temp directory if not present
        if not execPath == None:
            global BASE_PATH
            BASE_PATH = execPath
        if not os.path.isdir(self.tmpRoot):
            os.mkdir(self.tmpRoot)

        # load check object
        if self.deletion:
            self.check = Image.open(resource_path('img/deletemark.png'))
        else:
            self.check = Image.open(resource_path('img/checkmark.png'))
        self.check.thumbnail((40,40))

        # Prepare and load images
        self.images = images
        self.__PrepareImages()
        self.__LoadImages()
        self.SetSizer(self.mainSizer)
        self.SetAutoLayout(1)
        self.SetupScrolling(scroll_x=False, scroll_y=True)
        self.Fit()

    def GetSelection(self):
        selection = []
        for img in self.images:
            if img['checked']:
                selection.append(img['img_name'])
        return selection

    def GetCount(self):
        return len(self.images)

    def UpdateImages(self,files=None):
        self.mainSizer.Clear(True)
        if not files == None:
            self.images = files
            self.__PrepareImages()
        self.__LoadImages()
        self.SetAutoLayout(1)
        self.SetupScrolling(scroll_x=False, scroll_y=True)
        self.Fit()

    def SelectAll(self, event=None):
        for img in self.images:
            if not img['checked']:
                self.__ToggleImage(img)

    def UnselectAll(self, event=None):
        for img in self.images:
            if img['checked']:
                self.__ToggleImage(img)

    def __ToggleImage(self, image):
        imagePath = image['img_path'] + image['img_name']
        image["checked"] = not image["checked"]
        wxImage = self.__CheckOrUncheckImage(imagePath, image["checked"])
        image['img_ctrl'].SetBitmap(wx.BitmapFromImage(wxImage))

    def __PrepareImages(self):
        # if images are fresh loaded from player thumb creation needed, other wise not --> check image paths
        # always completely fresh set from player or complete set of thumbs
        thumbCreate = False
        for img in self.images:
            if not 'thumbs' in img['img_path']:
                # not thumb images
                thumbCreate = True
        if thumbCreate:
            dlg = False
            if len(self.images) > 5:
                dlg = True
                prgDlg = wx.ProgressDialog(tr("loading_previews"), tr("msg_loading_previews"))
                prgDlg.Pulse()

            # create clean temp path for images
            tmp = self.tmpRoot + 'tmp_thumbs_ssiv_' + str(self.id) + '/'
            if os.path.isdir(tmp):
                shutil.rmtree(tmp)
            os.mkdir(tmp)
            self.tmp = tmp
            for imgObj in self.images:
                imgPath = imgObj["img_path"] + imgObj['img_name']
                # get resized version of current image and save it temporary
                curImg = self.__SaveThumbnail(imgPath, self.imgWidth, imgObj['img_name'])
                imgObj["img_path"] = self.tmp
            if dlg:
                prgDlg.Update(100)
                if platform.system() == 'Windows':
                    prgDlg.Destroy()

    def __LoadImages(self):
        row = 0
        col = 0
        self.imgWidth = self.size[0] / self.cols - 4
        # load images and determine needed height for sizer
        for imgObj in self.images:
            imgPath = imgObj["img_path"] + imgObj['img_name']
            # get resized version of current image and save it temporary
            curImg = self.__CheckOrUncheckImage(imgPath, imgObj["checked"])
            curImgCtrl = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(curImg))
            imgObj['img_ctrl'] = curImgCtrl
            curImgCtrl.Bind(wx.EVT_LEFT_DOWN, lambda event, image=imgObj: self.ImageClicked(event,image))
            # print "Adding image in scrollable view at position (%d,%d)" % (row,col)
            self.mainSizer.Add(curImgCtrl,(row,col), flag=wx.ALL, border=2)

            # position for next image
            col = (col + 1) % self.cols
            if col == 0:
                row += 1

    def ImageClicked(self, event, image):
        self.__ToggleImage(image)


    def __CheckOrUncheckImage(self, imgPath, checked):
        img = Image.open(imgPath)
        alpha = 160
        if self.deletion:
            if not checked:
                alpha = 255
        else:
            if checked:
                alpha = 255
        img.putalpha(alpha)

        if checked:
            img.paste(self.check, (self.imgWidth - 42,2), self.check)
        return self.__PilToWxImage(img, img.size[0], img.size[1])


    def __SaveThumbnail(self, imgPath, width, filename):
        img = Image.open(imgPath)
        # scale the image, preserving the aspect ratio
        w = img.size[0]
        h = img.size[1]
        newW = width
        newH = width * h / w
        img.thumbnail((newW,newH))

        img.save(resource_path(self.tmp + filename))



    def __PilToWxImage(self, pilImage, w, h):
        image = wx.EmptyImage(w,h)
        image.SetData(pilImage.convert("RGB").tostring())
        image.SetAlphaData(pilImage.convert("RGBA").tostring()[3::4])
        return image

# HELPER METHOD to get correct resource path for image files
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
