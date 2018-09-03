#!/usr/bin/python
# load data from csv and munge it some
# 4/16/18
# updated 9/3/18

import csv
import logging
import numpy as np


class Data:

    paths = {
        'sea': '/home/pi/gitbucket/scroll/data/sea_level_rise.csv',
        'hot': '/home/pi/gitbucket/scroll/data/avg_hottest_day.csv',
        'precip': '/home/pi/gitbucket/scroll/data/precip_lowest_3_years_inches.csv'
    }

    def __init__(self, data_path=paths['sea']):
        self.logger = self._init_logger()
        self.data_path = data_path
        self.original_data = self._load_data()
        self.data = self._parse_data()
        self.x, self.y = self.data[:,0], self.data[:,1]
        self.f = self._estimate_function()
        self.integrals = self._compute_discrete_integrals()
        self.percents = self.calculate_percentages(datapoints=self.integrals)
        # self.normalized_data = self._normalize_data()

    def _init_logger(self):
        logger = logging.getLogger('data')
        logger.info('data logger instantiated')

        return logger

    def _load_data(self):
        '''return list of tuples with entries formatted as (x, y)'''
        self.logger.info('loading data from {}'.format(self.data_path))

        with open(self.data_path, 'r') as sheet:
            reader = csv.reader(sheet)
            next(reader, None)  # skip the header

            return [(float(row[0]), float(row[1])) for row in reader]

    def _parse_data(self):
        '''reset x-axis to between 0 and len(data) - 1 and represent data as numpy array'''
        self.logger.info('resetting x-axis to 0 - (len(data) - 1) and converting to numpy array')
        new_data = [(i, self.original_data[i][1]) for i in range(len(self.original_data))]
        return np.array(new_data)

    def _estimate_function(self, degree=3):
        '''
        estimate the function described by the dataset. z is a list of coefficients
        for the polynomial. these are returned as a numpy.poly1d object which
        represents the function in code.
        '''
        self.logger.info('estimating function from the datapoints')
        z = np.polyfit(self.x, self.y, degree)
        return np.poly1d(z)

    def _compute_discrete_integrals(self):
        '''
        compute the integral between each unit of x and return them in a list.
        the sum of the list is equal to the total area under the curve.
        '''
        self.logger.info('computing dicrete integrals between the datapoints')
        return [np.trapz([self.y[i], self.y[i + 1]], dx=1) for i in range(len(self.y)) if i < len(self.y) - 1]

    def calculate_percentages(self, datapoints):
        '''return list of percentages of each y datapoint of the total y dataset'''
        self.logger.info('calculating the percentages of discrete integrals to total integral')
        return [datapoints[i] / sum(datapoints) for i in range(len(datapoints))]

    def normalize_data(self, datapoints):
        '''return list of datapoints normalized between 0.0 - 1.0'''
        self.logger.info('normalizing the datapoints')
        data_min = min(datapoints)
        data_range = max(datapoints) - data_min

        return [(n - data_min) / data_range for n in datapoints]

    def translate(self, new_min=-1.0, new_max=1.0):
        '''
        translate normalized datapoints to range specified by new_min and new_max.
        defaults to a range of -1.0 to 1.0
        '''
        self.logger.info('translating normalized datapoints to new range of {} - {}'.format(new_min, new_max))
        return [new_min + (n * (new_max - new_min)) for n in self.normalized_data]

    def print_data(self):
        for datapoint in self.original_data:
            print('x: {}   y: {}'.format(datapoint[0], datapoint[1]))
            # self.logger.info('x: {}   y: {}'.format(datapoint[0], datapoint[1]))
