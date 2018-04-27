#!/usr/bin/python3
# control speed of a stepper motor with an arbitrary range of values
# 4/27/18

from data import Data
from stepper import Stepper


if __name__ == '__main__':
    # initialize the stepper motor
    pins = [4, 17, 27, 22]
    stepper = Stepper(pins)
    stppr = stepper.dynamic_step()
    stppr.send(None)

    # initialize the data set and convert it to a range of pauses
    my_data = Data()
    pauses = my_data.translate(new_min=0.1, new_max=0.005)

    # step through the range of pauses
    for i in range(len(pauses)):
        print('year = {}   feet = {}   pause = {}'.format(my_data.years[i], my_data.max_feets[i], pauses[i]))
        stppr.send(pauses[i])
