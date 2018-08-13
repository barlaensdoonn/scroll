#!/usr/bin/python
# load data from csv and munge it some
# 4/16/18
# updated 8/12/18

# TODO: fix logging

import csv
import logging
import numpy as np


class Data:

    sea_data_path = '/home/pi/gitbucket/scroll/yearly_sea_level_maxes.csv'

    def __init__(self, data_path=sea_data_path):
        self.logger = self._init_logger()
        self.data_path = data_path
        self.original_data = self._load_data()
        self.data = self._parse_data()
        self.x, self.y = self.data[:,0], self.data[:,1]
        self.f = self._estimate_function()
        self.integrals = self._compute_discrete_integrals()
        self.percents = self._calculate_percentages(datapoints=self.integrals)
        # self.normalized_data = self._normalize_data()

    def _init_logger(self):
        logger = logging.getLogger('data')
        logger.info('data logger instantiated')

        return logger

    def _load_data(self):
        '''return list of tuples with entries formatted as (x, y)'''
        with open(self.data_path, 'r') as sheet:
            reader = csv.reader(sheet)
            next(reader, None)  # skip the header

            return [(float(row[0]), float(row[1])) for row in reader]

    def _parse_data(self):
        '''reset x-axis to between 0 and len(data) - 1 and represent data as numpy array'''
        new_data = [(i, self.original_data[i][1]) for i in range(len(self.original_data))]
        return np.array(new_data)

    def _estimate_function(self, degree=3):
        '''
        estimate the function described by the dataset. z is a list of coefficients
        for the polynomial. these are returned as a numpy.poly1d object which
        represents the function in code.
        '''
        z = np.polyfit(self.x, self.y, degree)
        return np.poly1d(z)

    def _compute_discrete_integrals(self):
        '''
        compute the integral between each unit of x and return them in a list.
        the sum of the list is equal to the total area under the curve.
        '''
        return [np.trapz([self.y[i], self.y[i + 1]], dx=1) for i in range(len(self.y)) if i < len(self.y) - 1]

    def _calculate_percentages(self, datapoints=None):
        '''return list of percentages of each y datapoint of the total y dataset'''
        datapoints = self.y if not datapoints else datapoints
        return [datapoints[i] / sum(datapoints) * 100 for i in range(len(datapoints))]

    def _normalize_data(self, datapoints=None):
        '''return list of datapoints normalized between 0.0 - 1.0'''
        datapoints = self.y if not datapoints else datapoints
        data_min = min(datapoints)
        data_range = max(datapoints) - data_min

        return [(n - data_min) / data_range for n in datapoints]

    def translate(self, new_min=-1.0, new_max=1.0):
        '''
        translate normalized datapoints to range specified by new_min and new_max.
        defaults to a range of -1.0 to 1.0
        '''
        return [new_min + (n * (new_max - new_min)) for n in self.normalized_data]

    def print_data(self):
        for datapoint in self.original_data:
            print('x: {}   y: {}'.format(datapoint[0], datapoint[1]))
            # self.logger.info('x: {}   y: {}'.format(datapoint[0], datapoint[1]))
