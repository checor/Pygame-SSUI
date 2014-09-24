#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  main.py
#  
#  Copyright 2014 Sergio I. Urbina <checor@gmail.com>
#  
  
import threading, os, time

import screen, config, glob


def main():
    scr = screen.Screen()
    scr_t = threading.Thread(target=scr.run, args=('test.xml',))
    scr_t.start()
    while True:
        time.sleep(5)
        glob.numero_prueba += 1
    return 0

if __name__ == '__main__':
    main()

