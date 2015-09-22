#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#   http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.  See the License for the specific language
# governing permissions and limitations under the License.

#! /usr/bin/python


import sys
import os
import time
from PIL import Image
from PIL import ImageOps
from EPD import EPD
import RPi.GPIO as GPIO
from datetime import datetime 
import urllib

URL = "http://www.peanuts.com/wp-content/comic-strip/color-low-resolution/desktop/2015/daily/"
IMG_PREFIX =  "pe_c"
IMG_EXT = ".jpg"
STORE_PATH = "img"

is_button_pressed = False


def main(file_name):
    """main program - display list of images"""
    epd = EPD()
    liste = []
    # The display adapter has a button connected to pin 15
    # on the RaspberryPi pin list. Pin 15 is BCM GPIO22,
    # where BCM stands for Broadcom SoC.
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(22, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.add_event_detect(22, GPIO.FALLING, callback=button_pressed, bouncetime=300)

    epd.clear()
    
    file_name = get_img()

    #print('panel = {p:s} {w:d} x {h:d}  version={v:s}'.format(p=epd.panel, w=epd.width, h=epd.height, v=epd.version))

    #if not os.path.exists(file_name):
    #    sys.exit('error: image file{f:s} does not exist'.format(f=file_name))
    #print('display: {f:s}'.format(f=file_name))

    process_src_file(liste, file_name, epd.size)
    display_file(epd, liste)
        


def get_img():
    global URL
    global IMG_PREFIX
    global IMG_EXT

    now = datetime.now()
    img_suffix = now.strftime("%y%m%d")
    img_name = IMG_PREFIX + img_suffix + IMG_EXT
    
    filename = os.path.join(STORE_PATH, img_name)
    if not os.path.exists(filename):
        img_url = URL + img_name
        urllib.urlretrieve(img_url, filename)
    return filename
    

def process_src_file(liste, file_name, dst_size):
    image = Image.open(file_name)
    image = ImageOps.grayscale(image)


    w,h = image.size
    x = 0
    y = 0

    dst_width, dst_height = dst_size

    crop = image.crop((x, y, 210, h))
    crop = crop.convert("1", dither=Image.FLOYDSTEINBERG)
    strip = Image.new(crop.mode, dst_size, 1)
    strip.paste(crop, ((dst_width -  210) /2, (dst_height - h)/2))
    liste.append(strip)
        
    x = x + 210
    crop = image.crop((x, y, x + 215, h))
    crop = crop.convert("1", dither=Image.FLOYDSTEINBERG)
    strip = Image.new(crop.mode, dst_size, 1)
    strip.paste(crop, ((dst_width -  215) /2, (dst_height - h)/2))
    liste.append(strip)
    
    x = x + 215
    crop = image.crop((x, y, x + 215, h))
    crop = crop.convert("1", dither=Image.FLOYDSTEINBERG)
    strip = Image.new(crop.mode, dst_size, 1)
    strip.paste(crop, ((dst_width -  215) /2, (dst_height - h)/2))
    liste.append(strip)
    
    x = x + 215
    crop = image.crop((x, y, x + w - 640, h))
    crop = crop.convert("1", dither=Image.FLOYDSTEINBERG)
    strip = Image.new(crop.mode, dst_size, 1)
    strip.paste(crop, ((dst_width -  (w - 640)) /2, (dst_height - h)/2))
    liste.append(strip)


def button_pressed(channel):
    global is_button_pressed
    is_button_pressed = True


def display_file(epd, liste):
    """display centre of image then resized image"""
    global is_button_pressed
    index = 0
    while True:
        while True:
            if is_button_pressed:
                is_button_pressed = False
                break
        strip = liste[index % len(liste)]
        epd.display(strip)
        epd.update()
        time.sleep(3)
        index = index + 1
    
    
# main
if "__main__" == __name__:
    if len(sys.argv) !=  1:
        sys.exit('usage: {p:s}'.format(p=sys.argv[0]))
    main(sys.argv[1])
