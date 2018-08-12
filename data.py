#!/usr/bin/python
# load sea level data from csv
# 4/16/18
# updated 8/11/18

# TODO: fix logging

import csv
import logging
from collections import OrderedDict


class Data:

    sea_data_path = '/home/pi/gitbucket/scroll/yearly_sea_level_maxes.csv'

    def __init__(self, data_path=sea_data_path):
        self.logger = self._init_logger()
        self.data_path = data_path
        self.data = self._load_data()
        self.xs = [self.data[i][0] for i in range(len(self.data))]
        self.ys = [self.data[i][1] for i in range(len(self.data))]
        self.normalized_data = self._normalize_data()
        self.percents = self._calculate_percentages()

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

    def _normalize_data(self):
        '''return list of y datapoints normalized between 0.0 - 1.0'''
        data_min = min(self.ys)
        data_range = max(self.ys) - data_min

        return [(n - data_min) / data_range for n in self.ys]

    def _calculate_percentages(self):
        '''return list of percentages of each y datapoint of the total y dataset'''
        return [self.ys[i] / sum(self.ys) * 100 for i in range(len(self.ys))]

    def translate(self, new_min=-1.0, new_max=1.0):
        '''
        translate normalized datapoints to range specified by new_min and new_max.
        defaults to a range of -1.0 to 1.0
        '''
        return [new_min + (n * (new_max - new_min)) for n in self.normalized_data]

    def print_data(self):
        for datapoint in self.data:
            print('x: {}   y: {}'.format(datapoint, self.data[datapoint]))
            # self.logger.info('x: {}   y: {}'.format(datapoint, self.data[datapoint]))
