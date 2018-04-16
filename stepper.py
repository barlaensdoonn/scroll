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

    def step(self, pause=0.01):
        for sequence in self.sequences:
            for i in range(len(self.step_pins)):
                if sequence[i]:
                    # print('turning pin {} on'.format(step_pins[i].pin))
                    self.step_pins[i].on()
                else:
                    # print('turning pin {} off'.format(step_pins[i].pin))
                    self.step_pins[i].off()
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
