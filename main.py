#!/usr/bin/python
# control movement of a stepper motor by mapping discrete integrals of a dataset
# to motor steps
# 4/15/18
# updated 9/3/18

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
import sys
import time
import sqltrack
import argparse


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


def initialize_motors(feed_ip=None, eat_ip=None, sim=0):
    logger.info('''initializing motors''')
    Motors = namedtuple('Motors', ['feed', 'eat'])

    if sim == 1:
        motors = Motors
    else:
        init_motors = [stepperweblib.StepperControl(ip) for ip in [feed_ip, eat_ip]]
        motors = Motors(feed=init_motors[0], eat=init_motors[1])
        for motor in motors:
            motor.halt()

        # check if limit switch is engaged on eat motor; eat paper if it's not
        if not motors.eat.check_flag():  # limit switch not engaged == 1
            logger.warning('limit switch not engaged upon initialization')
            eat_paper(motors.eat)

    return motors


def feed_paper(motor, steps, speed=250, sim=0, dir=-1):
    steps *= dir  # rotate 'backwards'
    logger.info('moving feed motor {} steps at speed {}'.format(steps, speed))
    if sim == 0:
        motor.move_relative(speed, steps)

        while True:
            if motor.check_reached():
                motor.halt()
                logger.info('feed motor movement finished')
                break
            # need a delay
            time.sleep(0.1)


def eat_paper(motor, steps=500, speed=5, sim=0):
    '''
    move eat motor continuously until limit switch is engaged. steps defaults
    to 1/50th of a revolution, or 500 steps. speed defaults to a conservative 2
    '''
    logger.info('moving eat motor {} steps at speed {}'.format(steps, speed))
    if sim == 0:
        motor.move_relative(speed, steps)

        while True:
            if motor.check_flag():  # limit switch engaged == 0
                motor.halt()
                logger.info('limit switch engaged, motor halted')
                break
            elif motor.check_reached():
                logger.info('eat motor movement finished but limit switch not engaged... repeating movement')
                motor.move_relative(speed, steps)
            # need a delay
            time.sleep(0.1)


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
    tomorrow = today + timedelta(seconds=10)
    # tomorrow = today + timedelta(days=1)
    # tomorrow = tomorrow.replace(hour=12, minute=0, second=0, microsecond=0)
    waiter.wait_til(tomorrow)


if __name__ == '__main__':
    # add some command line
    parser = argparse.ArgumentParser(prog='testhelp.py')
    parser.add_argument('--config', default="config.yml", help='Configuration file in YAML')
    parser.add_argument('--sim', dest='sim', action='store_const', const=1, default=0, help='run the system in a simulation')
    args = parser.parse_args()

    sim = args.sim
    print("Using config: {}".format(args.config))

    # Load the yaml file
    with open(args.config, "r") as config_file:
        config = yaml.safe_load(config_file)

    # get the art name from yaml
    file = config["art"]
    feed_ip = config["feed_ip"]
    eat_ip = config["eat_ip"]
    feed_dir = int(config["feed_dir"])

    # put in all of the moves into a database
    sqltrack.create_database()

    logger = configure_logger(get_basepath(), get_hostname())
    # need to set IP by art piece -gary
    motors = initialize_motors(feed_ip=feed_ip, eat_ip=eat_ip, sim=sim)
    if sim == 0:
        waiter = Wait()

    if file in Data.paths.keys():
        ingredients = Data(data_path=Data.paths[file])
    else:
        # Data() uses sea level data by default
        ingredients = Data()

    kitchen = Compute(target_diameter=Compute.diameter_after_half_paper_moved)

    # distribute total_inches_to_move into meals based on how many datapoints we have,
    # and the percentage of their integrals to the total integral of the function.
    # determine how many portions are in a meal based on the total # of movements
    # divided by the # of meals.
    meals = [ingredients.percents[i] * kitchen.total_inches_to_move for i in range(len(ingredients.percents))]
    portions_per_meal = kitchen.total_num_movements / len(meals)
    steps_completed = 0
    move_sum = 0.0

    if sim == 1:
        outname = "move-{}.txt".format(file)
        movetest = open(outname, "w")
        outname = "radius-{}.txt".format(file)
        rtest = open(outname, "w")
        count = 0

    for i in range(len(meals)):
        meal = meals[i]
        logger.info('eating meal {} of {}'.format(i, len(meals) - 1))
        logger.info('breaking meal {} into {} daily portions'.format(i, portions_per_meal))
        portions = [meal / portions_per_meal for j in range(portions_per_meal)]

        for k in range(len(portions)):
            # break portions into 4 inch bites for the idler arm
            logger.info('breaking portion {} ({} inches) into bites'.format(k, portions[k]))
            bites = break_into_bites(portions[k])
            logger.info('eating portion {} of {}'.format(k, len(portions) - 1))

            # total all of the moves so far
            move_sum += portions[k]

            # check to see if that move was already made
            last_position = sqltrack.get_last_position()
            if(move_sum <= last_position):
                logger.warning('already ate portion at {} < {}'.format(move_sum, last_position))
                continue

            if sim == 1:
                count += 1
                movetest.write("{} {} {}\n".format(count, portions[k], len(bites)))

            for m in range(len(bites)):
                bite = bites[m]
                logger.info('eating bite {} of {} from portion {} of meal {}'.format(m, len(bites) - 1, k, i))

                # calculate steps per inches for the bite, and velocity for the motor.
                # then move.
                steps = int(kitchen.calculate_steps_per_inches(inches_to_move=bite))
                feed_outer_radius = kitchen.get_current_radius()
                feed_speed = kitchen.calculate_current_velocity(kitchen.current_circumference)
                feed_paper(motors.feed, steps=steps, speed=feed_speed, sim=sim, dir=feed_dir)
                steps_completed += steps

                # calculate outer radius for eat motor based on total paper moved, then
                # circumference of the eat roll, which we need to calculate motor speed.
                # then move.
                eat_outer_radius = kitchen.calculate_outer_radius(kitchen.total_inches_moved)
                eat_circumference = kitchen.calculate_circumference(eat_outer_radius)
                eat_speed = kitchen.calculate_current_velocity(eat_circumference)
                eat_paper(motors.eat, speed=eat_speed, sim=sim)
                if sim == 1:
                    rtest.write("{} {} {} {} {}\n".format(count, feed_outer_radius, feed_speed, eat_outer_radius, eat_speed))

            # track on the portion level when a move is completed
            sqltrack.add_move(datetime.today(), move_sum)

            logger.info('finished portion {}, getting sleepy...'.format(i))
            if sim == 0:
                sleep_tight(waiter)

        logger.info('finished meal {}, yum!!'.format(i))

    kitchen.log_test_results()
    logger.info('actual steps completed: {}'.format(steps_completed))
