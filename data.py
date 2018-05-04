#!/usr/bin/python3
# load sea level data from csv
# 4/16/18
# updated 4/26/18

import csv
import logging
from collections import OrderedDict


class Data:

    data_path = '/home/pi/gitbucket/scroll/yearly_sea_level_maxes.csv'

    def __init__(self):
        self.logger = self._init_logger()
        self.data = self._load_data()
        self.years = [year for year in self.data.keys()]
        self.max_feets = [float(value) for value in self.data.values()]
        self.normalized_feets = self._normalize_data()

    def _init_logger(self):
        logger = logging.getLogger('data')
        logger.info('data logger instantiated')

        return logger

    def _load_data(self):
        '''return ordered dict with entries formatted as year: max_sea_level_feet'''

        with open(self.data_path, 'r') as sheet:
            reader = csv.reader(sheet)
            next(reader, None)  # skip the header

            return OrderedDict([(row[0], row[1]) for row in reader])

    def _normalize_data(self):
        '''return list of sea_level_yearly_max datapoints normalized between 0.0 - 1.0'''

        data_min = min(self.max_feets)
        data_range = max(self.max_feets) - data_min

        return [(n - data_min) / data_range for n in self.max_feets]

    def translate(self, new_min=-1.0, new_max=1.0):
        '''
        translate normalized datapoints to range specified by new_min and new_max.
        defaults to a range of -1.0 to 1.0
        '''
        return [new_min + (n * (new_max - new_min)) for n in self.normalized_feets]

    def print_data(self):
        for datapoint in self.data:
            self.logger.info('year: {}   max_sea_level_feet: {}'.format(datapoint, self.data[datapoint]))
