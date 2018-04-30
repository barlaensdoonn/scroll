#!/usr/bin/python3
# control speed of a stepper motor by mapping pause time
# between steps to an arbitrary range of values
# 4/15/18
# updated 4/30/18

from time import sleep
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


def move(stepper, num_steps, pause):
    for i in range(num_steps):
        stepper.step(pause)


if __name__ == '__main__':
    # NOTE: instead of max_steps_per_move being a constant, the # of steps
    # per movement event will be dynamically calculated based on
    # the current circumference of the roll
    steppers = initialize_steppers()
    max_steps_per_move = 10

    # intialize data and convert original datapoints
    # into a range of pause values to use between motor steps
    my_data = initialize_data()
    pauses = my_data.translate(new_min=0.1, new_max=0.005)

    # step through the list of pause values
    for i in range(len(pauses)):
        print('year = {}   feet = {}   pause = {}'.format(my_data.years[i], my_data.max_feets[i], pauses[i]))

        # move the first motor a small number of steps to let out paper
        move(steppers['let_out'], max_steps_per_move, pauses[i])

        # TODO: this is where the limit switch would provide feedback
        sleep(1)

        # move the second motor a small number of steps to take in the paper that has been let out
        move(steppers['take_up'], max_steps_per_move, pauses[i])

        # NOTE: second limit switch provide feedback here?
        sleep(1)
