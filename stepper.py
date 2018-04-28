#!/usr/bin/python3
# control a stepper motor from RasPi with Adafruit TB6612 driver
# 4/27/18

from time import sleep
from gpiozero import OutputDevice


class Stepper:
    # each sequence represents a single step
    sequences = [
        [1, 0, 1, 0],
        [0, 1, 1, 0],
        [0, 1, 0, 1],
        [1, 0, 0, 1]
    ]

    def __init__(self, pins):
        self.pins = pins
        self.step_pins = [OutputDevice(pin) for pin in self.pins]
        self.driver = self._init_driver()

    def _init_driver(self):
        '''get the driver generator object ready to use'''

        driver = self._driver()
        driver.send(None)

        return driver

    def _sequencer(self):
        '''infinite generator to loop through the step sequences'''

        while True:
            for sequence in self.sequences:
                yield sequence

    def _step(self, sequence):
        '''ingest the step sequence and turn output pins on or off accordingly'''

        for i in range(len(self.step_pins)):
            self.step_pins[i].on() if sequence[i] else self.step_pins[i].off()

    def _driver(self):
        '''
        generator object for controlling the stepper motor.
        pause values are passed in via send() in the step() method.
        '''

        for sequence in self._sequencer():
            pause = yield
            self._step(sequence)
            sleep(pause)

    def step(self, pause=0.01):
        '''
        step the stepper by sending a pause time to the stepper driver generator object
        if this method is called without a pause time, it defaults to 10 milliseconds.
        '''

        self.driver.send(pause)

    def nongen_step(self, pause=0.01):
        '''
        the non-generator object way to step the stepper.

        this needs to be called in an external loop. it's just here for reference,
        will probably be removed in the near future.
        '''

        for sequence in self.sequences:
            self._step(sequence)
            sleep(pause)


if __name__ == '__main__':
    pins = [4, 17, 27, 22]  # GPIO pins used to control the stepper
    stepper = Stepper(pins)

    try:
        while True:
            stepper.step()
    except KeyboardInterrupt:
        print('...user exit received...')
