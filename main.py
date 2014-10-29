#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  main.py
#  
#  Copyright 2014 Sergio I. Urbina <checor@gmail.com>
#  
  
from multiprocessing import Process, freeze_support
import os
import time

import screen
import config
import glob


def main():
    freeze_support()
    scr = screen.Screen()
    scr_t = Process(target=scr.start, args=('min.yaml',))
    scr_t.start()
    
    #Test
    glob.set_variable('venta', 0)
    while True:
        time.sleep(.1)
        glob.var_sum('venta', .1)
        if glob.get_variable('venta') >= 30:
            break
    return 0

if __name__ == '__main__':
    main()
