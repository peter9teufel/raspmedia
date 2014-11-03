#! /usr/bin/env python

import os, sys, subprocess, time, shutil, Image, threading, random
import urllib2
from constants import *

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
    
    for file in os.listdir(USB_MEDIA_PATH):
        if not file.startswith('.'):
            if file.endswith((SUPPORTED_IMAGE_EXTENSIONS)):
                OptimizeAndCopyImage(file, USB_MEDIA_PATH, MEDIA_PATH)
            elif file.endswith((SUPPORTED_VIDEO_EXTENSIONS)):
                print "Copy video file: ", file
                size = (os.stat(USB_MEDIA_PATH + '/' + file).st_size)
                size /= 1024
                size /= 1024
                fileSize = str(size) + 'MB'
                print "Size: ", fileSize
                print "Please wait..."
                srcFile = USB_MEDIA_PATH + '/' + file
                dstFile = MEDIA_PATH + '/' + file
                shutil.copyfile(srcFile, dstFile)

    print "Media files copied to player successfully!"


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


# Main Method
def StartupRoutine():
    if UsbDrivePresent():
        print "USB device present"
        if RaspMediaFilesPresent():
            print "Media files found on USB device"
            CopyMediaFiles()
        else:
            print "No media files found on USB device"
    print "Startup routine finished, starting RaspMedia Player..."
    print "Bye bye..."

    os.system("sudo python rasp-mediaplayer.py")


StartupRoutine()
