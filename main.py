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
        motor.motor_halt()

    return motors[0], motors[1]


if __name__ == '__main__':
    logger = configure_logger(get_basepath(), get_hostname())
    waiter = Wait()
    feed_ip, eat_ip = '10.0.0.59', '10.0.0.62'
    feed, eat = initialize_motors(feed_ip, eat_ip)

    # today = datetime.today()
    # tomorrow = today + timedelta(days=1)
    # waiter.wait_til(tomorrow)

    movements = ['08:11:18:12:09:00', '08:11:18:12:08:30', '08:11:18:12:08:00']

    while movements:
        movement = movements.pop()
        waiter.wait_til(movement)

        feed.move_relative(200, 25000)
        while True:
            if feed.check_reached():
                feed.motor_halt()
                logger.info('feed motor movement finished')
                break

        eat_steps = 25000 - 5000
        eat.move_relative(200, eat_steps)
        while True:
            if eat.check_reached():
                if not eat.check_flag():
                    eat.motor_halt()
                    logger.info('eat motor movement finished')
                    break
                eat.move_relative(1, 1)
