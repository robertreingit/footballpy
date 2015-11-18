# -*- coding: utf-8 -*-
"""
test_dfl_parser: unittests for the dfl_parser_functions

The tests relies on the specific test files which are pruned
versions of original files.

@author: rein
@license: MIT
@version 0.1
"""

import unittest
import numpy as np
import impire_parser

class TestMatchPosition(unittest.TestCase):
    """Unit test class for the MatchPositionParser.
    """
    @classmethod
    def setUpClass(cls):
        cls.test_file = 'test/impire/123456.pos'

    def test_read_in_position(self):
        home,tmp2,tmp2 = impire_parser.read_in_position_data(TestMatchPosition.test_file)
        self.assertTrue(home.shape[0] == 11)


    def test_sort_raw_data(self):
        """Tests whether the raw data is sorted properly."""
        home,tmp,tmp2 = impire_parser.read_in_position_data(TestMatchPosition.test_file)
        home_s = impire_parser.sort_position_data(home)
        test_array = np.arange(7) + 1.0
        target_array = [d for d in home_s if np.all(d[:,0]==15.0)][0][:,1]
        self.assertTrue(np.all(target_array == test_array))


if __name__ == '__main__':
    unittest.main()
    
