# -*- coding: utf-8 -*-
"""
test_formation_quantifier: unittests for the formation_quantifier functions

@author: rein
@license: MIT
@version 0.1
"""

import unittest
import footballpy.processing.formation_quantifier as fq
import numpy as np

class TestReshapePosData(unittest.TestCase):
    """ Unit test class for the reshape_position_data function
    """
    @classmethod
    def setUpClass(cls):
        cls.__test_pos = np.ones((100,11,3))
        tmp1 = np.arange(22)
        tmp1.shape = (1,22)
        tmp2 = np.ones((100,1)).dot(tmp1)
        tmp2.shape = (100,11,2)
        cls.__test_pos[:,:,1:3] = tmp2
        cls.__test_ball = np.ones((100,6))
        cls.__test_ball[10,4] = -13
        cls.__test_ball[15,5] = -23
        cls.__test_half = np.ones((100,1))
        cls.__test_half[50:] = 2

    def test_matrix_shape(self):
        """Testing whether the returning matrix has correct shape.
        """
        res = fq.reshape_pos_data(TestReshapePosData.__test_pos,
            TestReshapePosData.__test_ball, TestReshapePosData.__test_half)
        self.assertEqual(res.shape,(100,26))

    def test_matrix_correct_metadata(self):
        """Testing whether the returning matrix has meta-date in correct
            position.
        """
        res = fq.reshape_pos_data(TestReshapePosData.__test_pos,
            TestReshapePosData.__test_ball, TestReshapePosData.__test_half)
        self.assertEqual(res[10,1], -13)
        self.assertEqual(res[15,2], -23)
        self.assertTrue(np.all(res[:50,3] == 1))
        self.assertTrue(np.all(res[50:,3] == 2))

    def test_correct_positiondata(self):
        """
        """
        res = fq.reshape_pos_data(TestReshapePosData.__test_pos,
            TestReshapePosData.__test_ball, TestReshapePosData.__test_half)
        self.assertTrue(np.all(res[:,10:12] == (6,7)))
        self.assertTrue(np.all(res[:,12:14] == (8,9)))
