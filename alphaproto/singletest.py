import stepperweblib
import sys
import time

host = "10.0.1.71"
control = stepperweblib.StepperControl(host)
control.MoveRelative(200, 25000)
count = 0
# Move and when it gets there, move again
stop = 0

while True:
    v = control.CheckReached()
    # if reached and not stopped, move again
    if v == 1 and stop == 0:
        control.MoveRelative(200, 25000)
        count = 0
    f = control.CheckFlag()
    # if flag is present, stop right away
    if f == 1:
        stop = 1
        control.MotorHalt()
    else:
        # restart, movement if previously stopped
        if stop == 1:
            stop = 0
            control.MoveRelative(200, 25000)
            count = 0

    count = count + 1
    print("Out: {}".format(count, v))
    sys.stdout.flush()
    time.sleep(.1)
