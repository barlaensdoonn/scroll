#!/usr/bin/python
# control movement of a stepper motor by mapping discrete integrals of a dataset
# to motor steps
# 4/15/18
# updated 8/15/18

import os
import yaml
import logging
import logging.config
from socket import gethostname
from collections import namedtuple
from datetime import datetime, timedelta
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
    logger.info('''initializing motors''')
    Motors = namedtuple('Motors', ['feed', 'eat'])
    init_motors = [stepperweblib.StepperControl(ip) for ip in [feed_ip, eat_ip]]
    motors = Motors(feed=init_motors[0], eat=init_motors[1])

    for motor in motors:
        motor.halt()

    # check if limit switch is engaged on eat motor; eat paper if it's not
    if motors.eat.check_flag():  # limit switch not engaged == 1
        logger.warning('limit switch not engaged upon initialization')
        eat_paper(motors.eat)

    return motors


def feed_paper(motor, steps, speed=250):
    steps *= -1  # rotate 'backwards'
    logger.info('moving feed motor {} steps at speed {}'.format(steps, speed))
    motor.move_relative(speed, steps)

    while True:
        if motor.check_reached():
            motor.halt()
            logger.info('feed motor movement finished')
            break


def eat_paper(motor, steps=500, speed=2):
    '''
    move eat motor continuously until limit switch is engaged. steps defaults
    to 1/50th of a revolution, or 500 steps. speed defaults to a conservative 2
    '''
    logger.info('moving eat motor {} steps at speed {}'.format(steps, speed))
    motor.move_relative(speed, steps)

    while True:
        if not motor.check_flag():  # limit switch engaged == 0
            motor.halt()
            logger.info('limit switch engaged, motor halted')
            break
        elif motor.check_reached() and motor.check_flag():
            logger.info('eat motor movement finished but limit switch not engaged... repeating movement')
            motor.move_relative(speed, steps)


def break_into_bites(portion, max_inches_per_bite=4):
    '''break portion into 4 inch bites for the idler arm, and append the remainder'''
    numbites = int(portion / max_inches_per_bite)  # int() always rounds down
    last_bite = portion % max_inches_per_bite

    bites = [4 for i in range(numbites)]
    bites.append(last_bite)

    return bites


def sleep_tight(waiter):
    '''sleep until the next showdown tomorrow at high noon'''
    today = datetime.today()
    tomorrow = today + timedelta(seconds=0.01)
    # tomorrow = today + timedelta(days=1)
    # tomorrow = tomorrow.replace(hour=12, minute=0, second=0, microsecond=0)
    waiter.wait_til(tomorrow)


if __name__ == '__main__':
    # TODO:
    # 1. read in total_steps_completed, meal #, and bite # from state file
    # 2. write total_steps_completed, meal #, and bite # to state file after every bite
    # 3. lower log rotator size
    logger = configure_logger(get_basepath(), get_hostname())
    motors = initialize_motors(feed_ip='10.0.0.59', eat_ip='10.0.0.62')
    waiter = Wait()
    ingredients = Data()
    kitchen = Compute(target_diameter=33.70645)  # 33.7 in is diameter of roll after half the paper has been unraveled

    meals = [ingredients.percents[i] * kitchen.total_inches_to_move for i in range(len(ingredients.percents))]
    portions_per_meal = kitchen.total_num_movements / len(meals)  # break the meals up into day size portions
    steps_completed = 0

    for i in range(len(meals)):
        meal = meals[i]
        logger.info('eating meal {} of {}'.format(i, len(meals) - 1))
        logger.info('breaking meal {} into {} daily portions'.format(i, portions_per_meal))
        portions = [meal / portions_per_meal for j in range(portions_per_meal)]

        for k in range(len(portions)):
            logger.info('breaking portion {} into bites'.format(k))
            bites = break_into_bites(portions[k])
            logger.info('eating portion {} of {}'.format(k, len(portions) - 1))

            for m in range(len(bites)):
                bite = bites[m]
                logger.info('eating bite {} of {} from portion {} of meal {}'.format(m, len(bites) - 1, k, i))

                steps = int(kitchen.calculate_steps_per_inches(inches_to_move=bite))
                feed_speed = kitchen.calculate_current_velocity(kitchen.current_circumference)
                feed_paper(motors.feed, steps=steps)  # will add speed here later, for now testing at max speed
                steps_completed += steps

                eat_outer_radius = kitchen.calculate_outer_radius(kitchen.total_inches_moved)
                eat_circumference = kitchen.calculate_circumference(eat_outer_radius)
                eat_speed = kitchen.calculate_current_velocity(eat_circumference)
                # eat_paper(motors.eat, speed=eat_speed)

            logger.info('finished portion {}, getting sleepy...'.format(i))
            sleep_tight(waiter)

        logger.info('finished meal {}, yum!!'.format(i))

    kitchen.log_test_results()
    logger.info('actual steps completed: {}'.format(steps_completed))
