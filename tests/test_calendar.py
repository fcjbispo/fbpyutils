'''
Unit tests for calendar utilities.
'''
from os import makedev
import unittest

from fbpyutils import calendar as cal
from datetime import datetime

class TestCalendar(unittest.TestCase):
    def test_calendar_creation(self):
        dt1 = datetime(2021, 1, 1)
        dt2 = datetime(2021, 12, 31)

        result = []
        
        calendar1 = cal.calendar(dt1, dt2)

        result.append(len(calendar1) > 0)

        self.assertTrue(all(result))


if __name__ == '__main__':
    unittest.main()