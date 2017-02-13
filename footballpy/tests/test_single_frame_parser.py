# -*- encoding: utf-8 -*-
"""
test_formation_quantifier: unittests for the formation_quantifier functions

@author: rein
@license: MIT
@version 0.1
"""
import unittest
import footballpy.fs.loader.single_frame_parser as sp
import numpy as np


class TestFloodArray(unittest.TestCase):
    """Unit tests for the flood array class.
    """

    def test_expansion(self):
        testArray = sp.FloodArray( 10, 2, 2 )
        for i in range(12):
            testArray.push((1.0, 2.0))
        res = testArray.data()    
        self.assertTrue(np.all(res.shape == (12,2)))
        self.assertTrue(np.all(res == (1.0, 2.0)))
