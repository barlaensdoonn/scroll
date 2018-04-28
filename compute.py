#!/usr/bin/python3
# control speed of a stepper motor by mapping pause time
# between steps to an arbitrary range of values
# 4/15/18
# updated 4/28/18

from math import pi


class PaperPusher:
    # paper constants
    diameter_start = 96  # starting with 8' diameter
    diameter_end = diameter_start / 2  # we want to move half the roll by the end
    width_of_paper = None  # don't know yet

    # motor constants
    steps_per_revolution = 200
    total_num_of_movements = 365 * 50  # 365 days times 50 years
    max_inches_per_move = 10  # max # of inches that can move based on the travel of the idler arm

    def __init__(self):
        self.steps_completed = 0
        self.num_revs_completed = self.get_num_revs_completed()
        self.total_revs_to_complete = self.get_total_num_revs()
        self.total_steps_to_complete = self.get_total_num_steps()
        self.current_diameter = self.get_current_diameter()
        self.current_circumference = self.get_current_circumference()
        self.inches_per_step = self.get_inches_per_step()

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
        number of revolutions times width of the paper
        '''
        return self.diameter_start - (self.num_revs_completed * self.width_of_paper)

    def get_current_circumference(self):
        '''
        current circuference is also the # of inches of paper
        that will move with a single revolution
        '''
        return self._get_circumference(self.current_diameter)

    def get_total_num_revs(self):
        '''
        total number of revolutions to complete should be the difference between
        the starting diameter and ending diameter divided by the width of the paper
        '''
        return (self.diameter_start - self.diameter_end) / self.width_of_paper

    def get_total_num_steps(self):
        '''
        total # of steps is total # of revolutions times steps per revolution
        '''
        return self.total_num_revolutions * self.steps_per_revolution

    def get_inches_per_step(self):
        '''
        the # of inches of paper that move with each step of the motor is equal
        to the current circumference divided by # of steps per full revolution
        '''
        return self.current_circumference / self.steps_per_revolution
