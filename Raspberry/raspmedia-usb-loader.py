#! /usr/bin/env python

import os, sys, subprocess, time, shutil, Image, threading, random, re
import urllib2
from constants import *
from packages.rmconfig import configtool

ROOT_PATH = "/home/pi/raspmedia/"
MEDIA_PATH = ROOT_PATH + "Raspberry/media"
USB_PATH = "/media/usb0/"
USB_MEDIA_PATH = USB_PATH + 'raspmedia'

def UsbDrivePresent():
    proc = subprocess.Popen(["ls /dev | grep 'sda'"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    if 'sda' in out:
        return True
    else:
        return False

def RaspMediaFilesPresent():
    # check if usb contains kiosk directory
    if os.path.isdir(USB_MEDIA_PATH):
        print "USB RaspMedia directory present"
        return True

def CopyMediaFiles():
    print "Copying files from USB to RaspMedia Player"
    clear = True
    # search for update indicator file
    for file in os.listdir(USB_MEDIA_PATH):
        if not file.endswith((SUPPORTED_IMAGE_EXTENSIONS)) and not file.endswith((SUPPORTED_VIDEO_EXTENSIONS)) and file.startswith('update'):
            # file indicating a file update found, load config and set flag
            print "File to indicate a media file update found."
            print "Current files on the player will not be deleted."
            print "Existing files with the same name as a new media file will be overwritten."
            clear = False
            config = configtool.readConfig()
            try:
                configDict = ast.literal_eval(config)
                config = configDict
            except:
                pass
            imgEnabled = config["image_enabled"]
            vidEnabled = config["video_enabled"]
    if clear:
        # delete previous files from player
        shutil.rmtree(MEDIA_PATH)
        if not os.path.isdir(MEDIA_PATH):
            os.mkdir(MEDIA_PATH)
        imgEnabled = 0
        vidEnabled = 0
    for file in os.listdir(USB_MEDIA_PATH):
        if not file.startswith('.'):
            if file.endswith((SUPPORTED_IMAGE_EXTENSIONS)):
                imgEnabled = 1
                ResizeFitAndCopyImage(file, USB_MEDIA_PATH, MEDIA_PATH)
                # OptimizeAndCopyImage(file, USB_MEDIA_PATH, MEDIA_PATH)
            elif file.endswith((SUPPORTED_VIDEO_EXTENSIONS)):
                vidEnabled = 1
                print "Copy video file: ", file
                size = (os.stat(os.path.join(USB_MEDIA_PATH, file)).st_size)
                size /= 1024
                size /= 1024
                fileSize = str(size) + 'MB'
                print "Size: ", fileSize
                print "Please wait..."
                srcFile = os.path.join(USB_MEDIA_PATH, file)
                newFileName = makeStringPlayerSafe(file)
                dstFile = os.path.join(MEDIA_PATH, newFileName)
                shutil.copyfile(srcFile, dstFile)

    print "Media files copied to player successfully!"
    print "Configuring playback settings for your new media files..."
    configtool.readConfig()
    configtool.setConfigValue("image_enabled", imgEnabled)
    configtool.setConfigValue("video_enabled", vidEnabled)
    print "Done!"

def ResizeFitAndCopyImage(fileName, basePath, destPath):
    targetWidth = 1920
    targetHeight = 1080
    ratio = 1. * targetWidth/targetHeight

    newFileName = makeStringPlayerSafe(fileName)

    filePath = os.path.join(basePath, fileName)
    destFilePath = os.path.join(destPath, newFileName)

    print "*********************************************************************************"
    img = Image.open(str(filePath))
    try:
        img.load()
    except IOError:
        print "IOError in loading PIL image while optimizing, filling up with grey pixels..."
    # check exif data if image was originally rotated
    #img = _checkOrientation(img)
    w,h = img.size
    if w == targetWidth and h == targetHeight:
        # no processing needed, just copy image
        print "Image already in 1920x1080, no optimization needed. Copying image to %s" % destFilePath
        shutil.copyfile(filePath, destFilePath)
    else:
        print "Image size does not match 1920x1080, optimizing image for player use..."
        if w/h > ratio:
            width = targetWidth
            height = targetWidth * h / w
        else:
            height = targetHeight
            width = targetHeight * w / h
        if width < w and height < h:
            img.thumbnail((width,height))
        else:
            img = img.resize((width, height))
        (imW, imH) = img.size

        offsetX = (targetWidth - imW) / 2
        offsetY = (targetHeight - imH) / 2

        new_im = Image.new('RGB', (targetWidth,targetHeight))
        new_im.paste(img, (offsetX, offsetY))
        print "Saving optimized image to %s" % destFilePath
        # save new image in destination path
        new_im.save(destFilePath, 'JPEG', quality=100)

def ResizeAndCopyImage(fileName, basePath, destPath):
    targetWidth = 1920
    targetHeight = 1080
    ratio = 1. * targetWidth/targetHeight

    filePath = basePath + '/' + fileName
    destFilePath = destPath + '/' + fileName

    im = Image.open(str(filePath)) # open the input file
    (width, height) = im.size        # get the size of the input image

    if width > height * ratio:
        # crop the image on the left and right side
        newwidth = int(height * ratio)
        left = width / 2 - newwidth / 2
        right = left + newwidth
        # keep the height of the image
        top = 0
        bottom = height
    elif width < height * ratio:
        # crop the image on the top and bottom
        newheight = int(width / ratio)
        top = height / 2 - newheight / 2
        bottom = top + newheight
        # keep the width of the impage
        left = 0
        right = width
    if width != height * ratio:
        im = im.crop((left, top, right, bottom))

    im = im.resize((targetWidth, targetHeight), Image.ANTIALIAS)
    
    print "Saving optimized image: %d x %d at path %s" % (targetWidth,targetHeight,destFilePath)
    if(fileName.endswith('.png') or fileName.endswith('.PNG')):
        im.save(destFilePath, 'PNG')
    else:
        im.save(destFilePath, 'JPEG', quality=100)


def OptimizeAndCopyImage(fileName, basePath, destPath, maxW=1920, maxH=1080, minW=400, minH=400):
    filePath = basePath + '/' + fileName
    destFilePath = destPath + '/' + fileName
    #print "Opening image " + filePath
    img = Image.open(str(filePath))
    try:
        img.load()
    except IOError:
        print "IOError in loading PIL image while optimizing, filling up with grey pixels..."
    # check exif data if image was originally rotated
    #img = _checkOrientation(img)
    w,h = img.size

    if w > maxW or h > maxH:
        if w/h > 1.770:
            width = maxW
            height = maxW * h / w
        else:
            height = maxH
            width = maxH * w / h
        if width < w and height < h:
            img.thumbnail((width,height))
        else:
            img = img.resize((width, height))
    elif w < minW or h < minH:
        if w/h > 1.770:
            width = minW
            height = minW * h / w
        else:
            height = minH
            width = minH * w / h
        if width < w and height < h:
            img.thumbnail((width,height))
        else:
            img = img.resize((width, height))
    else:
        width = w
        height = h
    print "Saving optimized image: %d x %d at path %s" % (width,height,destFilePath)
    if(fileName.endswith('.png') or fileName.endswith('.PNG')):
        img.save(destFilePath, 'PNG')
    else:
        img.save(destFilePath, 'JPEG', quality=90)

def makeStringPlayerSafe(string):
    # replace whitespaces due to compatibility with omxplayer
    string = re.sub('[ ]', '_', string)
    # replace special characters
    string = re.sub(u'[ö]', 'oe', string)
    string = re.sub(u'[ä]', 'ae', string);
    string = re.sub(u'[ü]', 'ue', string);
    string = re.sub(u'[!@#$%&§+*]', '', string);
    return string

# Main Method
def StartupRoutine():
    if UsbDrivePresent():
        print "USB device present"
        if RaspMediaFilesPresent():
            print "Media files found on USB device"
            CopyMediaFiles()
        else:
            print "No media files found on USB device"
    print ""
    print "Startup routine finished, starting RaspMedia Player..."
    print "Bye bye..."
    print ""

    time.sleep(2)

    os.system("sudo python rasp-mediaplayer.py > /dev/null")


StartupRoutine()
