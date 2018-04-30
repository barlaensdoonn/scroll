#!/usr/bin/python3
# control speed of a stepper motor by mapping pause time
# between steps to an arbitrary range of values
# 4/15/18
# updated 4/28/18

from data import Data
from stepper import Stepper


def initialize_data():
    return Data()


def initialize_steppers():
    pins = {
        'clockwise': [4, 17, 27, 22],
        'counter-clockwise': [5, 6, 13, 19]
    }

    steppers = {
        'let_out': Stepper(pins['clockwise'], direction='clockwise'),
        'take_up': Stepper(pins['counter-clockwise'], direction='counter-clockwise')
    }

    return steppers


if __name__ == '__main__':
    steppers = initialize_steppers()
    my_data = initialize_data()

    # convert datapoints into a range of pause values for stepper motor
    pauses = my_data.translate(new_min=0.1, new_max=0.005)

    # step through the list of pause values
    for i in range(len(pauses)):
        print('year = {}   feet = {}   pause = {}'.format(my_data.years[i], my_data.max_feets[i], pauses[i]))
        steppers['let_out'].step(pauses[i])
        steppers['take_up'].step(pauses[i])
