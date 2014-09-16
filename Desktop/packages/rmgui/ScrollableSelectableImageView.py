import wx, os, platform
from PIL import Image
import wx.lib.scrolledpanel as scrolled
import sys

################################################################################
# SCROLLABLE SELECTABLE IMAGE VIEW #############################################
################################################################################
class ScrollableSelectableImageView(scrolled.ScrolledPanel):
    def __init__(self,parent,id,size,images=[],cols=2,deletion=False):
        scrolled.ScrolledPanel.__init__(self,parent,id,size=size)
        self.parent = parent
        w = size[0] - 10
        self.size = (w,size[1])
        self.cols = cols
        self.deletion = deletion
        self.mainSizer = wx.GridBagSizer()
        abspath = os.path.abspath(__file__)
        dname = os.path.dirname(abspath)
        if self.deletion:
            self.check = Image.open(dname + 'ScrollableSelectableImageViewPNG/deletemark.png')
        else:
            self.check = Image.open(dname + 'ScrollableSelectableImageViewPNG/checkmark.png')
        self.check.thumbnail((40,40))
        self.images = images
        self.__LoadImages()
        self.SetSizer(self.mainSizer)
        self.SetAutoLayout(1)
        self.SetupScrolling(scroll_x=False, scroll_y=True)

    def GetSelection(self):
        selection = []
        for img in self.images:
            if img['checked']:
                selection.append(img['img_name'])
        return selection

    def __LoadImages(self):
        row = 0
        col = 0

        sizerH = 0
        maxH = 0

        self.imgWidth = self.size[0] / self.cols - 4
        images = []

        # load images and determine needed height for sizer
        for imgObj in self.images:
            imgPath = imgObj["img_path"] + imgObj['img_name']
            # get resized version of current image and save it temporary
            curImg = self.__ScaleImage(imgPath, self.imgWidth, imgObj["checked"])
            curImgCtrl = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(curImg))
            curImgCtrl.Bind(wx.EVT_LEFT_DOWN, lambda event, imagePath=imgPath, imgCtrl=curImgCtrl: self.ImageClicked(event,imagePath,imgCtrl))
            # print "Adding image in scrollable view at position (%d,%d)" % (row,col)
            self.mainSizer.Add(curImgCtrl,(row,col), flag=wx.ALL, border=2)

            # position for next image
            col = (col + 1) % self.cols
            if col == 0:
                row += 1

    def ImageClicked(self, event, imagePath,imgCtrl):
        for img in self.images:
            curPath = img["img_path"] + img["img_name"]
            if curPath == imagePath:
                img["checked"] = not img["checked"]
                wxImage = self.__ScaleImage(imagePath, self.imgWidth, img["checked"])
                imgCtrl.SetBitmap(wx.BitmapFromImage(wxImage))


    def __ScaleImage(self, imgPath, width, checked=False):
        img = Image.open(imgPath)
        # scale the image, preserving the aspect ratio
        w = img.size[0]
        h = img.size[1]

        newW = width
        newH = width * h / w
        img.thumbnail((newW,newH))

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



        image = wx.EmptyImage(newW,newH)
        image.SetData(img.convert("RGB").tostring())
        image.SetAlphaData(img.convert("RGBA").tostring()[3::4])


        return image
