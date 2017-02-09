# -*- coding: utf-8 -*-
"""
test_groupstats: unit tests for the test_groupsstats functions.

@author: rein
@license: MIT
@version: 0.1
"""

import unittest
import footballpy.analytics.groupstats as gr
import numpy as np

class TestGetTeamCentroid(unittest.TestCase):
    """Unit test class for the get_team_centroid function.
    """
    def test_correctedness_with_good_matrix(self):
        testData = np.ones((10,22))
        testData[:,0::2] = 10.0
        testData[:,1::2] = 20.0
        res = gr.get_team_centroid(testData)
        print res
        self.assertTrue(np.all(res[:,0] == 10.0))
        self.assertTrue(np.all(res[:,1] == 20.0))

    def test_correctedness_with_nan_matrix(self):
        testData = np.ones((10,22))
        testData[:,0::2] = 13.3
        testData[:,1::2] = 27.1
        testData[0,0] = np.NaN
        testData[0,3] = np.NaN
        testData[7,4] = np.NaN
        testData[8,7] = np.NaN
        res = gr.get_team_centroid(testData)
        print res
        self.assertTrue(np.all(res[:,0] == 13.3))
        self.assertTrue(np.all(res[:,1] == 27.1))
