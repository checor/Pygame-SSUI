#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  main.py
#  
#  Copyright 2014 Sergio I. Urbina <checor@gmail.com>
#  
  
import threading
import Queue
import os

import screen
import config

def main():
    q = Queue.Queue()  #Unused
    scr = screen.Screen()
    scr_t = threading.Thread(target=scr.run, args=('test.xml',))
    scr_t.start()
    return 0

if __name__ == '__main__':
    main()

