#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  wavves.py
#  
#  Copyright 2015 Sergio I. Urbina <checor@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

from screenutils import list_screens, Screen
import os

s= Screen("session1",True)

def start(wave, freq, gain, time ):
    global s
    com = "signalgen -A " + str(gain) + " -s 44100 -t " + str(time) + " " + str(wave) + " " + str(freq) 
    if os.uname()[4].startswith("arm"):
        pass
    else:
        com = "padsp " + com
    print com
    s.send_commands(com)
    
def stop():
    global s
    s.interrupt()

def spwm_start(hertz, period, runti):
	global s
	com = 'python spwm.py ' + str(hertz) + " " + str(period) + " " + str(runti)
	if os.uname()[4].startswith("arm"):
		s.send_commands(com)
