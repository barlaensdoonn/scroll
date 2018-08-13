#!/usr/bin/python
# control speed of a stepper motor by mapping pause time
# between steps to an arbitrary range of values
# 4/15/18
# updated 8/10/18

import os
import yaml
import logging
import logging.config
from socket import gethostname
from datetime import datetime, timedelta
import stepperweblib
from data import Data
from wait import Wait


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


def initialize_motors(feed_ip, eat_ip):
    motors = [stepperweblib.StepperControl(ip) for ip in [feed_ip, eat_ip]]

    for motor in motors:
        motor.halt()

    return motors[0], motors[1]


def feed_paper(steps, speed=200):
    steps *= -1  # rotate 'backwards'
    logger.info('moving feed motor {} steps'.format(steps))
    feed.move_relative(speed, steps)

    while True:
        if feed.check_reached():
            feed.halt()
            logger.info('feed motor movement finished')
            break


def eat_paper(steps=250000, speed=200):
    '''
    move eat motor continuously until limit switch is engaged. this will only
    work if idler arm + limit switch combo can tolerate the wind-down that occurs
    with motor.halt(). steps defaults to one full revolution, or 250,000 steps
    with a 10:1 gear ratio
    '''
    logger.info('moving eat motor {} steps'.format(steps))
    eat.move_relative(speed, steps)

    while True:
        if not eat.check_flag():  # limit switch engaged == 0
            eat.halt()
            logger.info('limit switch engaged, motor halted')
            break
        elif eat.check_reached() and eat.check_flag():
            logger.info('eat motor movement finished but limit switch not engaged... repeating movement')
            eat.move_relative(speed, steps)


def eat_paper_with_increment(motor, steps=250000, speed=200):
    '''
    move motor certain # of steps, then increment 1 step until limit switch engaged.
    this would be used if we precisely calculate # of steps to move eat motor each time.
    '''
    logger.info('moving eat motor {} steps'.format(steps))
    eat.move_relative(speed, steps)

    while True:
        if eat.check_reached():
            if not eat.check_flag():  # limit switch engaged == 0
                eat.halt()
                logger.info('limit switch engaged, motor halted')
                break
            eat.move_relative(1, 1)


if __name__ == '__main__':
    logger = configure_logger(get_basepath(), get_hostname())
    waiter = Wait()
    feed_ip, eat_ip = '10.0.0.59', '10.0.0.62'
    feed, eat = initialize_motors(feed_ip, eat_ip)

    # today = datetime.today()
    # tomorrow = today + timedelta(days=1)
    # waiter.wait_til(tomorrow)

    movements = ['18:49:00', '18:47:30', '18:47:00']

    while movements:
        movement = movements.pop()
        waiter.wait_til(movement)

        feed_paper(steps=25000)
        eat_paper(steps=25000)

        # feed.move_relative(200, 25000)
        # while True:
        #     if feed.check_reached():
        #         feed.halt()
        #         logger.info('feed motor movement finished')
        #         break
        #
        # eat_steps = 25000 - 5000
        # eat.move_relative(200, eat_steps)
        # while True:
        #     if eat.check_reached():
        #         if not eat.check_flag():
        #             eat.halt()
        #             logger.info('eat motor movement finished')
        #             break
        #         eat.move_relative(1, 1)
