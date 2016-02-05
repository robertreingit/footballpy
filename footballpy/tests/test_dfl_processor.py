# -*- coding: utf-8 -*-
"""
test_dfl_processor: unittests for the dfl_processor_functions

The tests relies on the specific test files which are pruned
versions of the original files.

@author: rein
@license: MIT
@version 0.1
"""

import unittest
import footballpy.processing.dfl_processor as dfl_processor
import numpy as np

class TestSortPosition(unittest.TestCase):
    """Unit test class for the dfl_parser.sort_position_data function.
    """
    def test_sorting_A(self):
        dummyData = [('A',1,'STZ'),('B',2,'DMZ'),('C',3,'LM')]
        self.assertEqual([dummyData[p] for p in [1,2,0]],
                dfl_processor.sort_position_data(dummyData))

    def test_sorting_B(self):
        dummyData = [('A',1,'M'),('B',2,'G'),('C',3,'A')]
        self.assertEqual([dummyData[p] for p in [1,0,2]],
                dfl_processor.sort_position_data(dummyData,'B'))

class TestDirectionTest(unittest.TestCase):
    """Unit test class for the dfl_parser.switch_playing_direction function.
    """
    def test_l2r(self):
        dummyData = np.zeros((10,3))
        dummyData[:,0] = np.arange(10)-10
        self.assertEqual(dfl_processor.determine_playing_direction(dummyData),'l2r')

