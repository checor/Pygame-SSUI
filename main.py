#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  main.py
#  
#  Copyright 2014 Sergio I. Urbina <checor@gmail.com>
#  
  
import threading, os, time

import screen
import config
import glob
import pickle
from screenutils import list_screens, Screen

settings = {}

def load_values(filename):
    settings = pickle.load( open("settings.txt", "rb"))
    glob.set_variable(sets, settings)
    

def main():
    
    scr = screen.Screen()
    scr_t = threading.Thread(target=scr.start, args=('piezo.yaml',))
    scr_t.start()
    
    #Test
    #glob.set_variable('venta', 0)
    
    #while True:
    #    time.sleep(.1)
    #    glob.var_sum('venta', .1)
    #    if glob.get_variable('venta') >= 30:
    #        break
    return 0

if __name__ == '__main__':
    main()
