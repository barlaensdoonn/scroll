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
        self.stepper = self._init_stepper()

    def _init_stepper(self):
        '''get the stepper generator object ready to use'''

        stppr = self._gen_step()
        stppr.send(None)

        return stppr

    def _sequencer(self):
        while True:
            for sequence in self.sequences:
                yield sequence

    def _step(self, sequence):
        for i in range(len(self.step_pins)):
            self.step_pins[i].on() if sequence[i] else self.step_pins[i].off()

    def _gen_step(self):
        for sequence in self._sequencer():
            pause = yield
            self._step(sequence)
            sleep(pause)

    def nongen_step(self, pause=0.01):
        '''
        the non-generator object way to step the stepper.

        this needs to be called in a while True loop.
        just here for reference, will probably be removed in the near future.
        '''

        for sequence in self.sequences:
            self._step(sequence)
            sleep(pause)

    def step(self, pause=0.01):
        self.stepper.send(pause)


if __name__ == '__main__':
    pins = [4, 17, 27, 22]
    stepper = Stepper(pins)

    try:
        while True:
            stepper.step()
    except KeyboardInterrupt:
        print('...user exit received...')
