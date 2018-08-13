#!/usr/bin/python
# control movement of a stepper motor by mapping discrete integrals of a dataset
# to motor steps
# 4/15/18
# updated 8/13/18

import os
import yaml
import logging
import logging.config
from socket import gethostname
from datetime import datetime, timedelta
from collections import deque
import stepperweblib
from wait import Wait
from data import Data
from compute import Compute


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


def initialize_motors(feed_ip=None, eat_ip=None):
    motors = [stepperweblib.StepperControl(ip) for ip in [feed_ip, eat_ip]]

    for motor in motors:
        motor.halt()

    return (motors[0], motors[1])


def feed_paper(motor, steps, speed=200):
    steps *= -1  # rotate 'backwards'
    logger.info('moving feed motor {} steps'.format(steps))
    motor.move_relative(speed, steps)

    while True:
        if motor.check_reached():
            motor.halt()
            logger.info('feed motor movement finished')
            break


def eat_paper(motor, steps=25000, speed=200):
    '''
    move eat motor continuously until limit switch is engaged. this will only
    work if idler arm + limit switch combo can tolerate the wind-down that occurs
    with motor.halt(). steps defaults to 1/10th revolution, or 25,000 steps
    with a 10:1 gear ratio.
    '''
    logger.info('moving eat motor {} steps'.format(steps))
    motor.move_relative(speed, steps)

    while True:
        if not motor.check_flag():  # limit switch engaged == 0
            motor.halt()
            logger.info('limit switch engaged, motor halted')
            break
        elif motor.check_reached() and eat.check_flag():
            logger.info('eat motor movement finished but limit switch not engaged... repeating movement')
            motor.move_relative(speed, steps)


def break_into_bites(meal, max_inches_per_bite=4):
    numbites = int(meal / max_inches_per_bite)  # int() always rounds down
    last_bite = meal % max_inches_per_bite

    bites = [4 for i in range(numbites)]
    bites.append(last_bite)

    return deque(bites)


def sleep_tight(waiter):
    '''sleep until the next showdown tomorrow at high noon'''
    today = datetime.today()
    tomorrow = today + timedelta(seconds=0.01)
    # tomorrow = today + timedelta(days=1)
    # tomorrow = tomorrow.replace(hour=12, minute=0, second=0, microsecond=0)
    waiter.wait_til(tomorrow)


if __name__ == '__main__':
    logger = configure_logger(get_basepath(), get_hostname())
    feed, eat = initialize_motors(feed_ip='10.0.0.59', eat_ip='10.0.0.62')
    waiter = Wait()
    ingredients = Data()
    kitchen = Compute()

    meals = [ingredients.percents[i] * kitchen.total_inches_to_move for i in range(len(ingredients.percents))]
    meals = deque(meals)
    steps_completed = 0

    for i in range(len(meals)):
        meal = meals[i]
        logger.info('eating meal {} of {}'.format(i, len(meals)))
        bites = break_into_bites(meal)

        for j in range(len(bites)):
            bite = bites[i]
            logger.info('eating bite {} of {} from meal {}'.format(j, len(bites), i))
            steps = int(kitchen.calculate_steps_per_inches(inches_to_move=bite))
            feed_paper(feed, steps=steps)
            steps_completed += steps
            # eat_paper(eat, steps=25000)

        logger.info('finished meal {}, getting sleepy...'.format(i))
        sleep_tight(waiter)

    logger.info('kitchen.total_steps_to_complete: {}'.format(kitchen.total_steps_to_complete))
    logger.info('kitchen.steps_completed: {}'.format(kitchen.steps_completed))
    logger.info('actual steps completed: {}'.format(steps_completed))
