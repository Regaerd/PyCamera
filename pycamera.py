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

    kDEPTH = 6

    def __init__(self, stdscr):
        self._palette = self._color_on = self.ascii_on = None
        self.stdscr = stdscr
        self.cam = cv.CaptureFromCAM(-1) # TODO support all availble cameras
        self.colors = None
        self.color_on = False
        self.ascii_on = True

        base_cache = [int(i / 256.0 * 6) for i in range(256)]
        self.r_cache = [r * self.kDEPTH * self.kDEPTH for r in base_cache]
        self.g_cache = [g * self.kDEPTH for g in base_cache]
        self.b_cache = [b + 1 for b in base_cache]
        self.verbose = False

    @property
    def palette(self): return self._palette
    @palette.setter
    def palette(self, value):
        self._palette = value
        self.palette_range = 256.0 / len(self._palette)

    @property
    def color_on(self): return self._color_on
    @color_on.setter
    def color_on(self, value):
        self._color_on = value # if self.ascii_on or value else True
        if not self.color_on: self.ascii_on = True
        self.init_colors()

    @property
    def ascii_on(self): return self._ascii_on
    @ascii_on.setter
    def ascii_on(self, value):
        self._ascii_on = value # if self.color_on or value else True
        if not self.ascii_on: self.color_on = True
        self.init_colors()

    def init_colors(self):
        div = (self.kDEPTH - 1) / 1000.0
        pair = 1
        try:
            for r in xrange(self.kDEPTH):
                for g in xrange(self.kDEPTH):
                    for b in xrange(self.kDEPTH):
                        curses.init_color(pair, int(r / div), int(g / div), int(b / div))
                        if self.ascii_on: curses.init_pair(pair, pair, 0)
                        else: curses.init_pair(pair, 0, pair)
                        pair = pair + 1

        except: # will fail for terminal that don't support 256 colors
            pass

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
        rgb = []
        try:
            for y in xrange(img.height):
                for x in xrange(img.width):
                    rgb = map(int, img[y, x])
                    if self.ascii_on:
                        index = int(sum(rgb) / 3.0 / self.palette_range)
                        char = self.palette[index]
                    else:
                        char = ' '

                    if self.color_on:
                        pair = self.r_cache[rgb[0]] + self.g_cache[rgb[1]] + self.b_cache[rgb[2]]
                        self.stdscr.addch(y, x, char, curses.color_pair(pair))
                    else:
                        self.stdscr.addch(y, x, char)
        except: # the last character will ERR
            pass

        if self.verbose:
            self.stdscr.clrtoeol()
            self.stdscr.addstr(0,0,'last color:q{}'.format(rgb))

    def view_resized(self):
        self.screen_h, self.screen_w = self.stdscr.getmaxyx()

    def next_palette(self):
        self.palette = self.kPALETTES[(self.kPALETTES.index(self.palette) + 1) % len(self.kPALETTES)]

    def toggle_color(self):
        self.color_on = not self.color_on

    def toggle_ascii(self):
        self.ascii_on = not self.ascii_on

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
        elif lower=='c': self.cam.toggle_color()
        elif lower=='a': self.cam.toggle_ascii()
        elif lower=='v': self.cam.verbose = not self.cam.verbose

def main(stdscr=None):
    if not stdscr: curses.wrapper(main)
    else:
        environ.setdefault('ESCDELAY', '25')
        Driver(stdscr).start()

if __name__ == '__main__': main()
