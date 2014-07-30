import wx, Image
import wx.lib.scrolledpanel as scrolled
import sys

################################################################################
# SCROLLABLE IMAGE VIEW ########################################################
################################################################################
class ScrollableImageView(scrolled.ScrolledPanel):
    def __init__(self,parent,id,size,images,cols=2):
        scrolled.ScrolledPanel.__init__(self,parent,id,size=size)
        self.parent = parent
        self.size = size
        self.cols = cols
        self.mainSizer = wx.GridBagSizer()
        self.images = images
        self.__LoadImages()
        self.SetSizer(self.mainSizer)
        self.SetAutoLayout(1)
        self.SetupScrolling(scroll_x=False, scroll_y=True)

    def __LoadImages(self):
        row = 0
        col = 0

        sizerH = 0
        maxH = 0

        imgWidth = self.size[0] / self.cols - 4
        images = []

        # load images and determine needed height for sizer
        for imgPath in self.images:
            # get resized version of current image and save it temporary
            curImg = self.__ScaleImage(imgPath, imgWidth)
            curImgCtrl = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(curImg))
            print "Adding image in scrollable view at position (%d,%d)" % (row,col)
            self.mainSizer.Add(curImgCtrl,(row,col), flag=wx.ALL, border=2)

            # position for next image
            col = (col + 1) % self.cols
            if col == 0:
                row += 1

    def __ScaleImage(self, imgPath, width):
        #img = wx.Image(imgPath)
        img = Image.open(imgPath)
        # scale the image, preserving the aspect ratio
        w = img.size[0]
        h = img.size[1]

        newW = width
        newH = width * h / w
        img.thumbnail((newW,newH))

        image = wx.EmptyImage(newW,newH)
        image.SetData(img.convert("RGB").tostring())
        image.SetAlphaData(img.convert("RGBA").tostring()[3::4])

        return image
