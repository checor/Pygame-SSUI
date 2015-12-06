#!/usr/bin/env python

# inverter.py
# 2015-03-04
# Public Domain

import sys
import time
import math

import pigpio

RUNTIME=30

HERTZ=20000
PERIOD=20000 # microseconds

GPIO=3

if len(sys.argv) > 1:
   hertz = int(sys.argv[1])
else:
   hertz = HERTZ

if len(sys.argv) > 2:
   period = int(sys.argv[2])
else:
   period = PERIOD

if len(sys.argv) > 3:
   runtime = int(sys.argv[3])
else:
   runtime = RUNTIME

pulse_width = 1000000 / hertz
steps = period / pulse_width

print("pw={} steps={} time={}".format(pulse_width, steps, runtime))

wf = []

for s in range(steps):
   angle = (s * math.pi) / steps
   duty_cycle = int((math.sin(angle) * pulse_width) + 0.5)

   print("s={} dc={}".format(s, duty_cycle))

   off_time = pulse_width - duty_cycle

   if duty_cycle:
      wf.append(pigpio.pulse(1<<GPIO, 0, duty_cycle)) # switch on

   if off_time:
      wf.append(pigpio.pulse(0, 1<<GPIO, off_time)) # switch off

pi = pigpio.pi() # Connect to local Pi.


pi.set_mode(GPIO, pigpio.OUTPUT)

pi.wave_clear()
pi.wave_add_generic(wf)
wid = pi.wave_create()

if wid >= 0:
   pi.wave_send_repeat(wid)
   time.sleep(runtime)
   pi.wave_tx_stop()
   pi.wave_delete(wid)

pi.stop()

