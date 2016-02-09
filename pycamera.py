#!/usr/bin/env python
# -*- coding: utf-8 -*-

__program__ = 'PyCamera'
__version__ = '0.5.0'
__description__ = 'Webcam terminal viewer'
__author__ = 'Brandon Dreager'
__author_email__ ='pycamera@subol.es'
__copyright__ = 'Copyright (c) 2016 Brandon Dreager'
__license__ = 'MIT'
__website__ = 'https://github.com/Regaerd/PyCamera'

import curses, cv
from os import environ

class PyCamera(object):
    kPALETTES = [list(' .,/c(@#8'),
                 list(' .;-:!>7?Co$QHNM'),
                 list(' .,:;irsXA253hMHGS#9B&@'),
                 list(' .,:;i1tfLCG08@'),
                 list(' .:-=+*#%@')]

    def __init__(self, stdscr):
        self._palette = None
        self.stdscr = stdscr
        self.cam = cv.CaptureFromCAM(0)

    @property
    def palette(self): return self._palette
    @palette.setter
    def palette(self, value):
        self._palette = value
        self.color_range = 256.0 / len(self._palette)

    def start(self):
        self.palette = self.kPALETTES[0]
        self.view_resized()

    def update(self):
        img = cv.QueryFrame(self.cam)
        thumbnail = cv.CreateImage((self.screen_w, self.screen_h), img.depth,  img.nChannels)
        cv.Resize(img, thumbnail)
        self.draw_img(thumbnail)
        self.stdscr.refresh()

    def draw_img(self, img):
        for x in xrange(img.height):
            for y in xrange(img.width):
                rgb = img[x, y]
                index = int(sum(rgb) / 3.0 / self.color_range)
                try: self.stdscr.addch(x, y, self.palette[index])
                except: pass

    def view_resized(self):
        self.screen_h, self.screen_w = self.stdscr.getmaxyx()

    def next_palette(self):
        self.palette = self.kPALETTES[(self.kPALETTES.index(self.palette) + 1) % len(self.kPALETTES)]

class Driver(object):
    kKEY_ESC = '\x1b'

    def __init__(self, stdscr):
        self.stdscr = stdscr
        curses.halfdelay(1)
        curses.curs_set(0)
        curses.use_default_colors()

        self.cam = PyCamera(stdscr)

        self.running = False

    def start(self):
        self.running = True
        self.cam.start()
        self.run()

    def run(self):
        while self.running:
            self.cam.update()
            self.update()

    def update(self):
        try:
            key = self.stdscr.getkey()
        except curses.error as e:
            if str(e) == 'no input': return
            raise e

        lower = key.lower()
        if key == 'KEY_RESIZE': self.cam.view_resized()
        elif key==self.kKEY_ESC or lower=='q': self.running = False
        elif lower=='p': self.cam.next_palette()

def main(stdscr=None):
    if not stdscr: curses.wrapper(main)
    else:
        environ.setdefault('ESCDELAY', '25')
        Driver(stdscr).start()

if __name__ == '__main__': main()
