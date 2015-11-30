# -*- coding: utf-8 -*-
"""
test_ragged_array: unittests for the ragged_array module


@author: rein
@license: MIT
@version 0.1
"""

import unittest
import ragged_array as ra
import numpy as np

class TestExpandRaggedArray(unittest.TestCase):
    """Unit test class for the expand_ragged_array_function
    """

    @classmethod
    def setUpClass(cls):
        # Some simple test data
        a1 = np.ones((4,2)); a1[:,0] = np.arange(4)
        a2 = 2*np.ones((6,2)); a2[:,0] = np.arange(6)
        a3 = 3*np.ones((2,2)); a3[:,0] = np.arange(4,6)
        cls.index = np.arange(6)
        cls.test_data = [a1,a2,a3]
        mis_id = -1.234567
        cls.mis_id = mis_id
        cls.expected_result = np.array([[1.,2.,mis_id],
                                    [1.,2.,mis_id],
                                    [1.,2.,mis_id],
                                    [1.,2.,mis_id],
                                    [mis_id,2.,3.0],
                                    [mis_id,2.,3.0]])

    def test_pitch_specs(self):
        obtained_result = ra.expand_indexed_ragged_array(
                TestExpandRaggedArray.test_data,
                TestExpandRaggedArray.index,
                missing_id=TestExpandRaggedArray.mis_id)
        self.assertTrue(np.all(obtained_result == self.expected_result))

    def test_accessor_function(self):
        """Tests whether the accessor function works."""
        test_data = [(i,data) for i,data in enumerate(self.test_data)]
        obtained_result = ra.expand_indexed_ragged_array(
                test_data,
                TestExpandRaggedArray.index,
                lambda x : x[1],
                TestExpandRaggedArray.mis_id)
        self.assertTrue(np.all(obtained_result == self.expected_result))

        
