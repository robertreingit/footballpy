# -*- encoding: utf-8 -*-
"""

@author: rein
@license: MIT
@version: 0.1
"""

import unittest
import numpy as np

from footballpy.processing.state_change import get_state_changes

class SimpleState(unittest.TestCase):
    """
    """

    def test_state_1(self):
        test_state = np.array([1,1,1,2,2,2,1,1,1,2,2,2])
        target = np.array([0, 3, 6, 9, 11])
        self.assertTrue(np.all(get_state_changes(test_state) == target))

    def test_state_2(self):
        test_state = np.array([1,1,1,2,2,2,3,3,3,3,2,2,2])
        target = np.array([0, 3, 6, 10, 12])
        self.assertTrue(np.all(get_state_changes(test_state) == target))

    def test_prepend_zero(self):
        test_state = np.array([1,1,1,2,2,2,1,1,1,2,2,2])
        target = np.array([3, 6, 9, 11])
        self.assertTrue(np.all(get_state_changes(test_state, prepend_zero=False) == target))

    def test_append_maxframe(self):
        test_state = np.array([1,1,1,2,2,2,1,1,1,2,2,2])
        target = np.array([0, 3, 6, 9])
        self.assertTrue(np.all(get_state_changes(test_state, append_max=False) == target))

    def test_prepend_appendf(self):
        test_state = np.array([1,1,1,2,2,2,1,1,1,2,2,2])
        target = np.array([3, 6, 9])
        self.assertTrue(np.all(get_state_changes(test_state, 
            prepend_zero = False, append_max=False) == target))


    def test_mulitple_states(self):
        test_state_1 = np.array([1,1,1,2,2,2,1,1,1,2,2,2])
        test_state_2 = np.array([1,1,1,2,2,2,3,3,3,2,2,2])
        target = np.array([0, 3, 6, 9, 11])
        self.assertTrue(np.all(get_state_changes(test_state_1, test_state_2) == target))

    def test_raise_varying_length(self):
        test_state_1 = np.array([1,1,1,2,2,2,1,1,1,2,2,2])
        test_state_2 = np.array([0,-1,-1,-1,0,0,0,0,0,-1,-1,-1,-1,-1])
        self.assertRaises(AssertionError, get_state_changes, test_state_1, test_state_2)

