#!/usr/bin/python
# class to calculate time to wait until some point in the future
# 5/3/18
# updated 8/10/18

import logging
from time import sleep
from datetime import datetime, timedelta


class Wait:
    '''
    class to handle sleeping until some point in the future.
    it uses time.sleep(), and therefore is blocking.

    there is one public method in this class, wait_til().
    read its docstring for details on how it's used.
    '''

    def __init__(self):
        self.logger = self._init_logger()
        self.format = '%m:%d:%y:%H:%M:%S'

    def _init_logger(self):
        logger = logging.getLogger('wait')
        logger.info('wait logger instantiated')

        return logger

    def _check_len(self, next_time):
        '''
        utility method to return # of fields separated by ':' in next_time.
        returns 1 if there is no ':' in next_time.
        '''
        return len(next_time.split(':'))

    def _parse(self, next_time):
        '''
        if next_time is already a datetime object, pass it on through.

        if next_time is a single field, treat it as an int representing seconds
        from now til some point in the future. attempt to add it to datetime.now()
        and return it.

        if next_time is 3 fields separated by ':', prepend it with the current date.
        otherwise leave it as is. either way attempt to convert it to datetime object.

        both int(next_time) and datetime.strptime(next_time, self.format) will
        throw ValueError if they fail due to bad arguments.
        '''
        if type(next_time) == datetime:
            return next_time
        else:
            next_time = str(next_time)
            check = self._check_len(next_time)

            try:
                if check == 1:
                    return datetime.now() + timedelta(seconds=int(next_time))
                elif check == 3:
                    today = datetime.today().strftime('%m:%d:%y')
                    next_time = ':'.join([today, next_time])
                return datetime.strptime(next_time, self.format)
            except ValueError:
                self.logger.error('improperly formatted input, cannot convert to datetime object')
                return None

    def _is_future(self, next_time):
        '''check that next_time is in the future'''

        if next_time > datetime.now():
            return next_time
        else:
            self.logger.error('input time is not in the future')
            return None

    def _validate_time(self, next_time):
        '''
        if seemingly valid input is received, attempt to parse it and convert it
        to a datetime object in the future; if input is invalid or this process
        fails somehow, return none
        '''
        next_time = self._parse(next_time)
        return self._is_future(next_time) if next_time else None

    def _calculate_wait(self, future):
        '''calculate total # of seconds between now and future for time.sleep()'''
        return (future - datetime.now()).total_seconds()

    def wait_til(self, next_time):
        '''
        next_time should be a string formatted in one of two ways, where
        each field is a zero padded decimal number assuming a 24-hour clock:

        1. 'month:day:year:hour:minute:second'
           i.e. '01:15:20:23:59:00' is Jan 15, 2020 at 11:59PM.
        2. 'hour:minute:second'
           omitting the first three fields will automatically set the date to the current date
           i.e. '23:59:00' is today's date at 11:59PM.

        alternatively pass in an int or a string representing the amount of seconds to pause.
        i.e. 20 will pause for 20 seconds, '120' will pause for 2 minutes, etc.
        '''
        valid_time = self._validate_time(next_time)

        if valid_time:
            sleeps = self._calculate_wait(valid_time)
            self.logger.info('pausing until {}, or {} seconds from now'.format(valid_time, sleeps))
            sleep(sleeps)
        else:
            self.logger.error('invalid input, unable to calculate wait time')
            self.logger.warning('sleeping for 30 seconds instead')
            self.wait_til(30)
