#!/usr/bin/python3
# control speed of a stepper motor with a range of values
# 4/15/18

from data import Data
from stepper import Stepper


if __name__ == '__main__':
    pins = [4, 17, 27, 22]
    stppr = Stepper(pins)

    my_data = Data()
    pauses = my_data.translate(new_min=0.1, new_max=0.005)

    for i in range(len(pauses)):
        print('year = {}   feet = {}   pause = {}'.format(my_data.years[i], my_data.max_feets[i], pauses[i]))
        stppr.step(pause=pauses[i])
