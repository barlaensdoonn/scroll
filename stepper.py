#!/usr/bin/python3
# control a stepper motor from RasPi with Adafruit TB6612 driver
# 4/15/18

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

    def _sequencer(self):
        while True:
            for sequence in self.sequences:
                yield sequence

    def _step(self, sequence):
        for i in range(len(self.step_pins)):
            self.step_pins[i].on() if sequence[i] else self.step_pins[i].off()

    def step(self, pause=0.01):
        for sequence in self.sequences:
            self._step(sequence)
            sleep(pause)


if __name__ == '__main__':
    pins = [4, 17, 27, 22]
    stepper = Stepper(pins)

    try:
        print('stepping the stepper...')
        while True:
            stepper.step()
            # print()
    except KeyboardInterrupt:
        print('...user exit received...')
