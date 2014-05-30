import wx, Image

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

def OptimizeImages(files, basePath, destPath, maxW=1920, maxH=1080, isWindows=True, style=OPT_CROP):
    prgDialog = wx.ProgressDialog("Optimizing images...", "Optimizing images for your player...", maximum=len(files), style=wx.PD_AUTO_HIDE)
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