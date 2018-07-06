#!/usr/bin/python3
# authored by Gary Stein at AlphaProto June 2018
# refactored for python 3 by Brandon Aleson July 2018
# updated 7/6/18

import sys
import time
import stepperweblib

host = "10.0.1.71"
control = stepperweblib.StepperControl(host)
control.move_relative(200, 25000)
count = 0
# Move and when it gets there, move again
stop = 0

while True:
    v = control.check_reached()
    # if reached and not stopped, move again
    if v == 1 and stop == 0:
        control.move_relative(200, 25000)
        count = 0
    f = control.check_flag()
    # if flag is present, stop right away
    if f == 1:
        stop = 1
        control.motor_halt()
    else:
        # restart, movement if previously stopped
        if stop == 1:
            stop = 0
            control.move_relative(200, 25000)
            count = 0

    count = count + 1
    print("Out: {}".format(count, v))
    sys.stdout.flush()
    time.sleep(.1)
