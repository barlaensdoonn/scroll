#!/usr/bin/python3
# control a stepper motor from RasPi with Adafruit TB6612 driver
# 4/15/18
# updated 4/27/18

import logging
from time import sleep
from gpiozero import OutputDevice


class Stepper:
    # moving from one phase to the next represents a single step
    phases = {
        'clockwise': [
            [1, 0, 1, 0],
            [0, 1, 1, 0],
            [0, 1, 0, 1],
            [1, 0, 0, 1]
        ],
        'counter-clockwise': [
            [1, 0, 0, 1],
            [0, 1, 0, 1],
            [0, 1, 1, 0],
            [1, 0, 1, 0]
        ]
    }

    def __init__(self, pins, direction='clockwise', logger_name='stepper'):
        self.logger = self._init_logger(logger_name)
        self.pins = pins
        self.step_pins = [OutputDevice(pin) for pin in self.pins]
        self.direction = direction
        self.driver = self._init_driver()

    def _init_logger(self, logger_name):
        logger = logging.getLogger(logger_name)
        logger.info('{} logger instantiated'.format(logger_name))

        return logger

    def _init_driver(self):
        '''initialize the driver generator object'''
        driver = self._driver()
        driver.send(None)

        return driver

    def _sequencer(self):
        '''infinite generator to loop through the step phases'''

        while True:
            for phase in self.phases[self.direction]:
                yield phase

    def _step(self, phase):
        '''ingest the step phase and turn output pins on or off accordingly'''

        for i in range(len(self.step_pins)):
            self.step_pins[i].on() if phase[i] else self.step_pins[i].off()

    def _driver(self):
        '''
        generator object for controlling the stepper motor.
        pause values are passed in via send() in the step() method.
        '''

        for phase in self._sequencer():
            pause = yield
            self._step(phase)
            sleep(pause)

    def step(self, pause=0.01):
        '''
        step the stepper by sending a pause time to the stepper driver generator object
        if this method is called without a pause time, it defaults to 10 milliseconds.
        '''
        self.driver.send(pause)

    def nongen_step(self, pause=0.01):
        '''
        the non-generator object way to step the stepper which needs to be called
        in an external loop. it's just here for reference, will probably be removed in the near future.
        '''

        for phase in self.phases:
            self._step(phase)
            sleep(pause)


if __name__ == '__main__':
    pins = [4, 17, 27, 22]  # GPIO pins used to control the stepper
    stepper = Stepper(pins)

    try:
        while True:
            stepper.step()
    except KeyboardInterrupt:
        print('...user exit received...')
