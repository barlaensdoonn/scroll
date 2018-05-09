#!/usr/bin/python3
# formulas to calculate properties of a roll of paper
# and map them to geared stepper motor movements
# 4/15/18
# updated 5/7/18

import logging
from math import pi


class Compute:
    '''
    a roll of paper is technically an Archimedean spiral (thanks Richard at AlphaProto!!),
    but since the paper's thickness is very small relative to its length, we can
    treat it as a roll of nested concentric circles, as we do in get_total_num_revs()

    for a discussion of the problem see this link:
    https://web.archive.org/web/20131103150639/http://mtl.math.uiuc.edu/special_presentations/JoansPaperRollProblem.pdf

    there are two approaches for calculating the target diameter in this case:
    1. target_diameter equals half the entire roll's diameter. this will end up
       moving more than half the total paper on the roll since the inner support
       core of the roll contains no paper. this is the approach taken below.
    2. if instead we want to move precisely half the paper on the roll, we would
       calculate target_diameter based on how many revolutions it would take
       to move exactly half the linear feet of paper on the roll.
    '''

    # paper constants - measurement units are inches
    paper_thickness = 0.0062
    roll_width = 4.5
    core_diameter = 4  # outer diameter of roll's supporting core is 4in
    core_radius = core_diameter / 2
    initial_diameter = 47.5
    initial_radius = initial_diameter / 2

    # motor constants
    steps_per_revolution = 200  # step angle of 1.8deg
    gear_ratio = 10 / 1
    geared_steps_per_revolution = steps_per_revolution * gear_ratio
    total_num_of_movements = 365 * 50  # 365 days times 50 years (placeholder, currently unknown)
    max_inches_per_move = 10  # max inches that can move based on the travel of the idler arm (placeholder, currently unknown)

    def __init__(self, target_diameter=(initial_diameter / 2)):
        '''
        set target_diameter to core_diameter to run simulation of unravelling
        the entire roll of paper. see class dosctring for explanation of
        why target_diameter defaults to initial_diameter / 2
        '''
        self.logger = self._init_logger()
        self.target_diameter = target_diameter
        self.target_radius = target_diameter / 2
        self.steps_completed = 0
        self.total_inches_moved = 0
        self.num_revs_completed = self.get_num_revs_completed()
        self.current_radius = self.get_current_radius()
        self.current_circumference = self.get_current_circumference()
        self.inches_per_step = self.get_inches_per_step()
        self.inches_per_geared_step = self.get_inches_per_geared_step()

        # these attrs mainly for testing, may be removed in the future
        self.total_revs_to_complete = self.get_total_num_revs(self.target_radius)
        self.total_steps_to_complete = self.get_total_num_steps()
        self.total_geared_steps_to_complete = self.total_steps_to_complete * self.gear_ratio
        self.total_num_layers = self.get_total_num_layers()
        self.total_linear_inches = self.get_total_linear_inches()

    def _init_logger(self):
        logger = logging.getLogger('compute')
        logger.info('compute logger instantiated')

        return logger

    def _get_circumference(self, radius):
        '''C = 2πr = πd'''
        return 2 * pi * radius

    def get_num_revs_completed(self):
        '''
        # of revolutions completed is # of steps completed
        divided by # of steps per revolution
        '''
        return self.steps_completed / self.geared_steps_per_revolution

    def get_current_radius(self):
        '''
        current radius should be starting radius minus
        number of revolutions times thickness of the paper
        '''
        return self.initial_radius - (self.num_revs_completed * self.paper_thickness)

    def get_current_circumference(self):
        '''
        current circuference is also the # of inches of paper
        that will move with a single revolution
        '''
        return self._get_circumference(self.current_radius)

    def get_inches_per_step(self):
        '''
        the # of inches of paper that move with each step of the motor is equal
        to the current circumference divided by # of steps per full revolution
        '''
        return self.current_circumference / self.steps_per_revolution

    def get_inches_per_geared_step(self):
        '''same as get_inches_per_step() but with the gear ratio applied'''
        return self.current_circumference / self.geared_steps_per_revolution

    def get_total_num_revs(self, target_radius):
        '''
        total number of revolutions to complete should be the difference between
        the starting radius and target radius divided by the width of the paper.
        if we set radius_end to core_radius, this is equivalent to
        the # of nested concentric circles that the roll contains.
        '''
        return (self.current_radius - target_radius) / self.paper_thickness

    def get_total_num_layers(self):
        '''
        total # of layers - or nested concentric circles - of paper on the roll
        is equal to the # of revolutions required to unravel the roll
        '''
        return self.get_total_num_revs(target_radius=self.core_radius)

    def get_total_num_steps(self):
        '''
        total # of steps is total # of revolutions times steps per revolution
        '''
        return self.total_revs_to_complete * self.steps_per_revolution

    def get_total_linear_inches(self):
        '''
        if we treat the roll as a series of nested concentric circles, then
        the total linear inches of paper on the roll is the average layer length
        times the total # of layers of paper. the average layer length is the
        circumference of the average radius
        '''
        average_radius = (self.initial_radius + self.core_radius) / 2
        average_layer_length = self._get_circumference(average_radius)

        return self.get_total_num_layers() * average_layer_length

    def print_attrs(self):
        '''debug purposes only'''
        print('steps completed: {}'.format(self.steps_completed))
        print('total inches moved: {}'.format(self.total_inches_moved))
        print('revolutions completed: {}'.format(self.num_revs_completed))
        print('current radius: {}'.format(self.current_radius))
        print('current circumference: {}'.format(self.current_circumference))
        print('inches per step: {}'.format(self.inches_per_step))
        print('inches per geared step: {}'.format(self.inches_per_geared_step))

    def log_attrs(self):
        '''debug purposes only'''
        self.logger.debug('steps completed: {}'.format(self.steps_completed))
        self.logger.debug('total inches moved: {}'.format(self.total_inches_moved))
        self.logger.debug('revolutions completed: {}'.format(self.num_revs_completed))
        self.logger.debug('current radius: {}'.format(self.current_radius))
        self.logger.debug('current circumference: {}'.format(self.current_circumference))
        self.logger.debug('inches per step: {}'.format(self.inches_per_step))
        self.logger.debug('inches per geared step: {}'.format(self.inches_per_geared_step))

    def print_totals(self):
        '''debug purposes only'''
        print('total # of layers: {}'.format(self.total_num_layers))
        print('total linear inches of paper: {}'.format(self.total_linear_inches))
        print('total linear feet of paper: {}'.format(self.total_linear_inches / 12))
        print('total revs to complete: {}'.format(self.total_revs_to_complete))
        print('total steps to complete: {}'.format(self.total_steps_to_complete))
        print('total geared steps to complete: {}'.format(self.total_geared_steps_to_complete))

    def update(self):
        self.steps_completed += 1
        self.total_inches_moved += self.inches_per_geared_step
        self.num_revs_completed = self.get_num_revs_completed()
        self.current_radius = self.get_current_radius()
        self.current_circumference = self.get_current_circumference()
        self.inches_per_step = self.get_inches_per_step()
        self.inches_per_geared_step = self.get_inches_per_geared_step()

    def _run(self):
        '''debug purposes only'''
        for i in range(int(self.total_geared_steps_to_complete)):
            self.update()
            self.print_attrs()
            print()


if __name__ == '__main__':
    push = Compute(target_diameter=Compute.core_diameter)
    push._run()
