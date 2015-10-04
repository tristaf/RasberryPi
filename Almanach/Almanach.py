#!/usr/bin/python
# -*- coding: latin-1 -*-

import sys
import os
from PIL import Image
from PIL import ImageOps
from PIL import ImageDraw
from PIL import ImageFont
from datetime import datetime
import time
from EPD import EPD
import urllib2, urllib
import json

WHITE = 1
BLACK = 0

# fonts are in different places on Raspbian/Angstrom so search
possible_fonts = [
    '/usr/share/fonts/truetype/ttf-dejavu/DejaVuSansMono-Bold.ttf',   # R.Pi
    '/usr/share/fonts/truetype/freefont/FreeMono.ttf',                # R.Pi
    '/usr/share/fonts/truetype/LiberationMono-Bold.ttf',              # B.B
    '/usr/share/fonts/truetype/DejaVuSansMono-Bold.ttf',              # B.B
    '/usr/share/fonts/TTF/FreeMonoBold.ttf',                          # Arch
    '/usr/share/fonts/TTF/DejaVuSans-Bold.ttf'                        # Arch
]


FONT_FILE = ''
for f in possible_fonts:
    if os.path.exists(f):
        FONT_FILE = f
        break

if '' == FONT_FILE:
    raise 'no font file found'


DAY_FONT_SIZE  = 100
MONTH_FONT_SIZE  = 20
TEMP_FONT_SIZE = 20

MAX_START = 0xffff

def main(argv):
    """main program - draw and display a test image"""

    epd = EPD()

    #print('panel = {p:s} {w:d} x {h:d}  version={v:s}'.format(p=epd.panel, w=epd.width, h=epd.height, v=epd.version))

    epd.clear()

    demo(epd)


def get_weather(woeid):
    baseurl = "https://query.yahooapis.com/v1/public/yql?"
    yql_query = "select item.condition from weather.forecast where woeid=" + woeid
    yql_url = baseurl + urllib.urlencode({'q':yql_query}) + "&format=json"
    result = urllib2.urlopen(yql_url).read()
    data = json.loads(result)
    code = data['query']['results']['channel']['item']['condition']['code']
    temp = data['query']['results']['channel']['item']['condition']['temp']
    return code, temp


def demo(epd):
    """simple partial update demo - draw draw a clock"""

    
    # initially set all white background
    image = Image.new('1', epd.size, WHITE)

    # prepare for drawing
    draw = ImageDraw.Draw(image)
    width, height = image.size

    day_font = ImageFont.truetype(FONT_FILE, DAY_FONT_SIZE)
    month_font = ImageFont.truetype(FONT_FILE, MONTH_FONT_SIZE)
    temp_font = ImageFont.truetype(FONT_FILE, TEMP_FONT_SIZE)

    # clear the display buffer
    draw.rectangle((0, 0, width, height), fill=WHITE, outline=WHITE)
    previous_second = 0
    previous_day = 0

    now = datetime.today()
    draw.rectangle((2, 2, width - 2, height - 2), fill=WHITE, outline=BLACK)
#draw.text((10, 55), '{y:04d}-{m:02d}-{d:02d}'.format(y=now.year, m=now.month, d=now.day), fill=BLACK, font=date_font)
    draw.text((75, 5), '{y:s}'.format(y=now.strftime('%B')), fill=BLACK, font=month_font)
    draw.text((5, 25), '{y:s}'.format(y=now.strftime('%d')), fill=BLACK, font=day_font)

    
    code, temp = get_weather("619163")
    temp_celsius = int(round(((int(temp) - 32) / 1.8), 0)) 
    if int(code) < 10:
        code = "0" + code
    weather = Image.open("Weather_icons/simple_weather_icon_" + code + ".png")
    #weather = ImageOps.grayscale(weather)
    w,h = weather.size
    new_w = epd.width / 4
    new_h = new_w * h / w
    weather = weather.resize((new_w, new_h))
    #weather = weather.convert("1", dither=Image.FLOYDSTEINBERG)
    offset = (epd.width / 2 + 30, 40)
    image.paste(weather, offset)
    draw.text((epd.width / 2 + 30, 100),'{t:d}°C'.format(t=temp_celsius), fill=BLACK, font=temp_font)
    

    epd.display(image)
    epd.update()    # full update every minute


# main
if "__main__" == __name__:
    if len(sys.argv) < 1:
        sys.exit('usage: {p:s}'.format(p=sys.argv[0]))

    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        sys.exit('interrupted')
        pass
