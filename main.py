#!/usr/bin/python3
# control speed of a stepper motor by mapping pause time
# between steps to an arbitrary range of values
# 4/15/18
# updated 5/3/18

import os
import yaml
import logging
import logging.config
from gpiozero import Button
from socket import gethostname
from data import Data
from wait import Wait
from stepper import Stepper


def _get_logfile_name(basepath, hostname):
    '''format log file as "hostname.log"'''

    return os.path.join(basepath, '{}.log'.format(hostname))


def _init_logger():
    logger = logging.getLogger('main')
    logger.info('main logger instantiated')

    return logger


def get_basepath():
    return os.path.dirname(os.path.realpath(__file__))


def get_hostname():
    return gethostname().split('.')[0]


def configure_logger(basepath, hostname):
    with open(os.path.join(basepath, 'log.yaml'), 'r') as log_conf:
        log_config = yaml.safe_load(log_conf)

    log_config['handlers']['file']['filename'] = _get_logfile_name(basepath, hostname)
    logging.config.dictConfig(log_config)
    logging.info('* * * * * * * * * * * * * * * * * * * *')
    logging.info('logging configured')

    return _init_logger()


def init_limit_switch():
    switch_pin = 12
    switch = Button(switch_pin)
    switch.when_pressed = lambda: logger.info('limit switch engaged')

    return switch


def init_steppers():
    pins = {
        'clockwise': [4, 17, 27, 22],
        'counter-clockwise': [5, 6, 13, 19]
    }

    steppers = {
        'let_out': Stepper(pins['clockwise'], direction='clockwise', logger_name='stepper-let_out'),
        'take_up': Stepper(pins['counter-clockwise'], direction='counter-clockwise', logger_name='stepper-take_up')
    }

    return steppers


def move(stepper, num_steps, pause):
    logger.info('moving {} stepper {} steps'.format(stepper, num_steps))

    for i in range(num_steps):
        steppers[stepper].step(pause)


def increment_to_limit(stepper, pause, switch):
    logger.info('incrementing {} stepper by one step until limit switch is engaged'.format(stepper))

    while not switch.is_pressed:
        steppers[stepper].step(pause)


if __name__ == '__main__':
    logger = configure_logger(get_basepath(), get_hostname())
    waiter = Wait()
    switch = init_limit_switch()

    # NOTE: instead of max_steps_per_move being a constant, the # of steps
    # per movement event will be dynamically calculated based on
    # the current circumference of the roll
    steppers = init_steppers()
    max_steps_per_move = 10

    # intialize data and convert original datapoints
    # into a range of pause values to use between motor steps
    my_data = Data()
    pauses = my_data.translate(new_min=0.1, new_max=0.005)

    # step through the list of pause values
    for i in range(len(pauses)):
        logger.info('year = {}   feet = {}   pause = {}'.format(my_data.years[i], my_data.max_feets[i], pauses[i]))

        # move the first motor a number of steps to let out paper
        move('let_out', max_steps_per_move, pauses[i])
        waiter.wait_til(1)

        # move the take up motor a smaller number of steps than the first motor
        # to account for differences in winding tightness
        move('take_up', int(max_steps_per_move * 0.8), pauses[i])

        # increment stepper until limit switch is engaged
        increment_to_limit('take_up', pauses[i], switch)
        waiter.wait_til(1)
