import wx, Image
from packages.lang.Localizer import *

SUPPORTED_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.JPG', '.JPEG', '.png', '.PNG')
OPT_CROP = 1
OPT_FIT = 2

def _optimizeCrop(fileName, basePath, destPath, maxW, maxH):
    filePath = basePath + '/' + fileName
    destFilePath = destPath + '/' + fileName
    if filePath.endswith((SUPPORTED_IMAGE_EXTENSIONS)):
        #print "Opening image " + filePath
        img = Image.open(str(filePath))
        try:
            img.load()
        except IOError:
            print "IOError in loading PIL image while optimizing, filling up with grey pixels..."
        maxW = 1920
        maxH = 1080
        w,h = img.size
        if w/h < 1.770:
            width = maxW
            height = maxW * h / w
        else:
            height = maxH
            width = maxH * w / h
        img.thumbnail((width, height))
        #print "Saving optimized image..."
        #print "W: ", width
        #print "H: ", height
        print "Imagesize %d x %d" % (width, height)
        if width == 1920:
            print "Cropping height"
            # crop upper and lower part
            diff = height - 1080
            img = img.crop((0,diff/2,width,height-diff/2))
        else:
            print "Cropping width"
            # crop left and right part
            diff = width - 1920
            img = img.crop((diff/2,0,width-diff/2,height))
        img.save(destFilePath, 'JPEG', quality=90)

def _optimizeFit(fileName, basePath, destPath, maxW, maxH):
    filePath = basePath + '/' + fileName
    destFilePath = destPath + '/' + fileName
    if filePath.endswith((SUPPORTED_IMAGE_EXTENSIONS)):
        #print "Opening image " + filePath
        img = Image.open(str(filePath))
        try:
            img.load()
        except IOError:
            print "IOError in loading PIL image while optimizing, filling up with grey pixels..."
        # check exif data if image was originally rotated
        img = _checkOrientation(img)
        maxW = 1920
        maxH = 1080
        w,h = img.size
        if w/h > 1.770:
            width = maxW
            height = maxW * h / w
        else:
            height = maxH
            width = maxH * w / h
        img.thumbnail((width, height))
        #print "Saving optimized image..."
        #print "W: ", width
        #print "H: ", height
        img.save(destFilePath, 'JPEG', quality=90)

def _checkOrientation(img):
    try :
        for orientation in ExifTags.TAGS.keys() :
            if ExifTags.TAGS[orientation]=='Orientation' : break
        exif=dict(img._getexif().items())

        if   exif[orientation] == 3 :
            img=img.rotate(180, expand=True)
        elif exif[orientation] == 6 :
            img=img.rotate(270, expand=True)
        elif exif[orientation] == 8 :
            img=img.rotate(90, expand=True)
    except:
        pass
        # print "Exif data not present or can not be processed, returning unmodified image..."
    return img

def OptimizeImages(files, basePath, destPath, maxW=1920, maxH=1080, isWindows=True, style=OPT_FIT):
    prgDialog = wx.ProgressDialog(tr("optimizing"), tr("optimizing_images"), maximum=len(files), style=wx.PD_AUTO_HIDE)
    cnt = 0
    for filename in files:
        if style == OPT_CROP:
            _optimizeCrop(filename, basePath, destPath, maxW, maxH)
        elif style == OPT_FIT:
            _optimizeFit(filename, basePath, destPath, maxW, maxH)
        cnt += 1
        prgDialog.Update(cnt)
    if isWindows:
        prgDialog.Destroy()

def DrawCaptionOntoBitmap( graphicFilename, captionTxt ) :

    # Create a dc "canvas" onto which the caption text will be drawn
    #  in order to get the text's extent (size).
    trialBmap_size = (160, 160)     # any size larger than the expexted text extent.
    textTrial_bmap = wx.EmptyBitmap( *trialBmap_size )
    dc = wx.MemoryDC( textTrial_bmap )

    txtPos = (5, 5)                     # an offset so the text doesn't get clipped
    dc.DrawText( captionTxt, *txtPos )
    txtWid, txtHgt = dc.GetTextExtent( captionTxt )
    print '--Caption text: ', captionTxt
    print '--Text size = ', txtWid, txtHgt
    dc.SelectObject( wx.NullBitmap )        # done with this dc; not used again
    
    #----------------------------------

    # Draw the caption on the file graphic bitmap.

    imgBmap = wx.Image( graphicFilename, wx.BITMAP_TYPE_ANY ).ConvertToBitmap()
    bmapSizeX, bmapSizeY = imgBmap.GetSize()
    print '--imgBmap Size = ', bmapSizeX, bmapSizeY

    # Create a dc "canvas" onto which the caption text  will be drawn
    dc = wx.MemoryDC( imgBmap )
    dc.SetBrush(wx.Brush(wx.Colour(0,0,0),wx.SOLID))
    dc.SetTextForeground(wx.WHITE)

    # Draw text at the bottom of the bitmap
    txtPosX = (bmapSizeX - txtWid) / 2
    txtPosY = bmapSizeY - txtHgt
    dc.DrawText( captionTxt, txtPosX, txtPosY )

    # Done doing text drawingdrawing.
    dc.SelectObject( wx.NullBitmap )        # Done with this dc

    return imgBmap
