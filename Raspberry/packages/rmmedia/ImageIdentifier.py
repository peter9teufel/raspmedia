from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import os

def IdentifyImage(name, ip=None):
    img = Image.open(os.getcwd() + '/raspidentify.jpg')
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(os.getcwd() + '/font/ethnocentric.ttf',80)
    #name = "RaspMedia"
    #ip = "192.168.1.110"
    nameSize = draw.textsize(name, font=font)
    print "NAMESIZE: ",nameSize
    nameX = 960 - (nameSize[0] / 2)
    nameY = 500
    if ip:
        nameY = 450
    draw.rectangle([(nameX - 10, nameY - 10),(nameX + nameSize[0] + 10, nameY + nameSize[1] + 10)], fill=(0,0,0))
    draw.text((nameX,nameY), name, (255,255,255),font=font)

    if ip:
        ipSize = draw.textsize(ip, font=font)
        ipX = 960 - (ipSize / 2)
        draw.rectangle([(ipX - 10, ipY - 10),(ipX + ipSize[0] + 10, ipY + ipSize[1] + 10)], fill=(0,0,0))
        draw.text((ipX,525), ip, (255,255,255), font=font)
    img.save('raspidentified.jpg')
