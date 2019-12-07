#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import argparse

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT

import paho.mqtt.client as mqtt

def showResult(score, num_all, num_yes, num_no):
    # base configuration of matrix device
    n = 4 #matrix view
    block_orientation = 90
    rotate = 0
    inreverse = True

    # create matrix device
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, cascaded=n or 1, block_orientation=block_orientation,
                     rotate=rotate or 0, blocks_arranged_in_reverse_order=inreverse)
    print("Created device")

    ##### show countdown
    print("Show countdown")
    words = [
        "5", "4", "3", "2", "1", " "
    ]
    virtual = viewport(device, width=device.width, height=len(words) * 8)
    with canvas(virtual) as draw:
        for i, word in enumerate(words):
            text(draw, ((device.width/(n*2))*(((n*2)-1)//2), i * 8), word, fill="white")
    for i in range(virtual.height - device.height):
        virtual.set_position((0, i))
        time.sleep(0.05)
        if i%8 == 0:
            time.sleep(0.6)

    ##### configure result
    score_text = str(score) + '%'
    results = [score_text, str(num_all), str(num_yes), str(num_no)]
    for i, item in enumerate(results):
        addSpace = 4-len(item)
        for j in range(addSpace):
            item = ' ' + item
        results[i] = item
    score_text = results[0]

    ##### show result
    print(score_text)
    with canvas(device) as draw:
        text(draw, (0, 0), score_text, fill="white")
    time.sleep(3)
    print(str(num_all) + " / " + str(num_yes) + " / " + str(num_no))
    show_message(device, str(num_all) + " / " + str(num_yes) + " / " + str(num_no), fill="white")

def test():
    print("hogehoge")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='yesno arguments',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--score', '-p', type=int, default=0, help='Percentage of Yes')
    parser.add_argument('--all',   '-a', type=int, default=0, help='Number of answers')
    parser.add_argument('--yes',   '-y', type=int, default=0, help='Number of answer "Yes"')
    parser.add_argument('--no',    '-n', type=int, default=0, help='Number of answer "No"')

    args = parser.parse_args()

    try:
        showResult(args.score, args.all, args.yes, args.no)
    except KeyboardInterrupt:
        pass
