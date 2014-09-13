#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  main.py
#  
#  Copyright 2014 Sergio I. Urbina <checor@gmail.com>
#  
  
import threading
import Queue

import screen

def main():
    #q = Queue.Queue()
    scr = screen.Screen()
    scr_t = threading.Thread(target=scr.run, args=())
    scr_t.start()
    return 0

if __name__ == '__main__':
    main()

