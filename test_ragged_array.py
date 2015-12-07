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

class TestIndexedRaggedArray(unittest.TestCase):
    """Unit test class for the expand_ragged_array_function
    """

    @classmethod
    def setUpClass(cls):
        """Generate some simple test data."""
        # Some simple test data
        a1 = np.ones((4,2)); a1[:,0] = np.arange(4)
        a2 = 2*np.ones((6,2)); a2[:,0] = np.arange(6)
        a3 = 3*np.ones((2,2)); a3[:,0] = np.arange(4,6)
        cls.index = np.arange(6)
        cls.test_data = [a1,a2,a3]
        mis_id = -1.234567
        cls.mis_id = mis_id
        cls.exp_arr = np.array([[1.,2.,mis_id],
                                    [1.,2.,mis_id],
                                    [1.,2.,mis_id],
                                    [1.,2.,mis_id],
                                    [mis_id,2.,3.],
                                    [mis_id,2.,3.]])

    def test_expand_function(self):
        """Tests simple expansion example."""
        obtained_result = ra.expand_indexed_ragged_array(
                self.test_data,
                self.index,
                missing_id=self.mis_id)
        self.assertTrue(np.all(obtained_result == self.exp_arr))

    def test_expand_accessor_function(self):
        """Tests whether the accessor function works."""
        test_data = [(i,data) for i,data in enumerate(self.test_data)]
        obtained_result = ra.expand_indexed_ragged_array(
                test_data,
                self.index,
                lambda x : x[1],
                TestIndexedRaggedArray.mis_id)
        self.assertTrue(np.all(obtained_result == self.exp_arr))

    def test_condense_function(self):
        """Tests whether the condense function works as expected."""
        test_data = self.exp_arr
        expect = np.array([[1.,2.],[1.,2.],[1.,2.],[1.,2.],[2.,3.],[2.,3.]])
        obtained = ra.condense_expanded_ragged_array(test_data)
        self.assertTrue(np.all(obtained == expect))

    def test_drop_function1(self):
        """Tests simple case."""
        mis_id = self.mis_id
        test_data = np.array([[1.,.2,mis_id],
            [1.,2.,mis_id],
            [1.,2.,3.],
            [mis_id,2.,3.]])
        expect = test_data.copy()
        expect[2,2] = mis_id
        obtained = ra.drop_expanded_ragged_entries(test_data, 2)
        self.assertTrue(np.all(obtained == expect))

    def test_drop_function2(self):
        """Tests simple case."""
        mis_id = self.mis_id
        test_data = np.array([[1.,.2,mis_id],
            [1.,2.,3.],
            [1.,2.,3.],
            [mis_id,2.,3.]])
        expect = test_data.copy()
        expect[2,2] = mis_id
        expect[1,2] = mis_id
        obtained = ra.drop_expanded_ragged_entries(test_data, 2)
        self.assertTrue(np.all(obtained == expect))

    def test_drop_function3(self):
        """Tests simple case."""
        mis_id = self.mis_id
        test_data = np.array([[1.,.2,mis_id,mis_id],
            [1.,2.,mis_id,mis_id],
            [1.,mis_id,3.,4.],
            [mis_id,2.,3.,4.],
            [mis_id,2.,3.,4.]])
        expect = np.array([[1.,.2,mis_id,mis_id],
            [1.,2.,mis_id,mis_id],
            [1.,mis_id,3.,mis_id],
            [mis_id,2.,3.,mis_id],
            [mis_id,2.,3.,mis_id]])
        obtained = ra.drop_expanded_ragged_entries(test_data, 2)
        self.assertTrue(np.all(obtained == expect))

    def test_drop_function3(self):
        """Tests simple case."""
        mis_id = self.mis_id
        test_data = np.array([[1.,.2,mis_id,mis_id],
            [1.,2.,mis_id,mis_id],
            [mis_id,mis_id,3.,4.],
            [mis_id,mis_id,3.,4.],
            [mis_id,mis_id,3.,4.]])
        expect = np.array([[1.,.2,mis_id,mis_id],
            [1.,2.,mis_id,mis_id],
            [mis_id,mis_id,3.,4.],
            [mis_id,mis_id,3.,4.],
            [mis_id,mis_id,3.,4.]])
        obtained = ra.drop_expanded_ragged_entries(test_data, 2)
        self.assertTrue(np.all(obtained == expect))
