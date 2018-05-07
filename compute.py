#!/usr/bin/python3
# formulas to calculate properties of a roll of paper
# and map them to stepper motor movements
# 4/15/18
# updated 5/6/18

'''
a roll of paper is technically an Archimedean spiral, but since the paper's
thickness is very small relative to its length, we can treat it as a roll
of nested concentric circles. for a discussion of the problem see this link:
https://web.archive.org/web/20131103150639/http://mtl.math.uiuc.edu/special_presentations/JoansPaperRollProblem.pdf
'''

import logging
from math import pi
from time import sleep


class Compute:
    # paper constants - measurement units are inches
    roll_width = 4.5
    core_diameter = 4
    paper_thickness = 0.0062
    diameter_start = 47.5  # starting with ~4' diameter
    # diameter_end = diameter_start / 2  # we want to move half the roll by the end
    diameter_end = core_diameter

    # motor constants
    steps_per_revolution = 200
    total_num_of_movements = 365 * 50  # 365 days times 50 years
    max_inches_per_move = 10  # max # of inches that can move based on the travel of the idler arm

    def __init__(self):
        # TODO: add total_inches_to_move, total_inches_moved
        # self.logger = self._init_logger()
        self.steps_completed = 0
        self.total_inches_moved = 0
        self.num_revs_completed = self.get_num_revs_completed()
        self.current_diameter = self.get_current_diameter()
        self.current_circumference = self.get_current_circumference()
        self.inches_per_step = self.get_inches_per_step()
        self.total_revs_to_complete = self.get_total_num_revs()  # this attr mainly for testing, may be removed in the future
        self.total_steps_to_complete = self.get_total_num_steps()  # this attr mainly for testing, may be removed in the future

    def _init_logger(self):
        logger = logging.getLogger('compute')
        logger.info('compute logger instantiated')

        return logger

    def _get_circumference(self, diameter):
        '''C = 2πr = πd'''
        return pi * diameter

    def get_num_revs_completed(self):
        '''
        # of revolutions compelted is # of steps completed
        divided by number of steps per revolution
        '''
        return self.steps_completed / self.steps_per_revolution

    def get_current_diameter(self):
        '''
        current diameter should be starting diameter minus
        number of revolutions times thickness of the paper
        '''
        return self.diameter_start - (self.num_revs_completed * self.paper_thickness)

    def get_current_circumference(self):
        '''
        current circuference is also the # of inches of paper
        that will move with a single revolution
        '''
        return self._get_circumference(self.current_diameter)

    def get_inches_per_step(self):
        '''
        the # of inches of paper that move with each step of the motor is equal
        to the current circumference divided by # of steps per full revolution
        '''
        return self.current_circumference / self.steps_per_revolution

    def get_total_num_revs(self):
        '''
        total number of revolutions to complete should be the difference between
        the starting diameter and ending diameter divided by the width of the paper
        '''
        return (self.current_diameter - self.diameter_end) / self.paper_thickness

    def get_total_num_steps(self):
        '''
        total # of steps is total # of revolutions times steps per revolution
        '''
        return self.total_revs_to_complete * self.steps_per_revolution

    def print_attrs(self):
        print('steps completed: {}'.format(self.steps_completed))
        print('total inches moved: {}'.format(self.total_inches_moved))
        print('revolutions completed: {}'.format(self.num_revs_completed))
        print('current diameter: {}'.format(self.current_diameter))
        print('current circumference: {}'.format(self.current_circumference))
        print('inches per step: {}'.format(self.inches_per_step))
        print('revs to complete: {}'.format(self.total_revs_to_complete))
        print('steps to complete: {}'.format(self.total_steps_to_complete))

    def log_attrs(self):
        self.logger.debug('steps completed: {}'.format(self.steps_completed))
        self.logger.debug('total inches moved: {}'.format(self.total_inches_moved))
        self.logger.debug('revolutions completed: {}'.format(self.num_revs_completed))
        self.logger.debug('current_diameter: {}'.format(self.current_diameter))
        self.logger.debug('current_circumference: {}'.format(self.current_circumference))
        self.logger.debug('inches per step: {}'.format(self.inches_per_step))
        self.logger.debug('revs to complete: {}'.format(self.total_revs_to_complete))
        self.logger.debug('steps to complete: {}'.format(self.total_steps_to_complete))

    def update(self):
        self.steps_completed += 1
        self.total_inches_moved += self.inches_per_step
        self.num_revs_completed = self.get_num_revs_completed()
        self.current_diameter = self.get_current_diameter()
        self.current_circumference = self.get_current_circumference()
        self.inches_per_step = self.get_inches_per_step()
        self.total_revs_to_complete = self.get_total_num_revs()
        self.total_steps_to_complete = self.get_total_num_steps()
        self.print_attrs()

    def _run(self):
        '''debug purposes only'''

        for i in range(int(self.total_steps_to_complete)):
            self.update()
            print()
            # sleep(0.5)


if __name__ == '__main__':
    push = Compute()
    push._run()
