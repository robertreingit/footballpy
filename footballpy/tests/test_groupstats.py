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

    def test_correct_shape(self):
        testData = np.ones((10,22))
        testData[:,0::2] = 10.0
        testData[:,1::2] = 20.0
        res = gr.get_team_centroid(testData)
        self.assertTrue(np.all((10, 2) == res.shape))


    def test_correctedness_with_good_matrix(self):
        testData = np.ones((10,22))
        testData[:,0::2] = 10.0
        testData[:,1::2] = 20.0

        res = gr.get_team_centroid(testData)
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
        self.assertTrue(np.all(res[:,0] == 13.3))
        self.assertTrue(np.all(res[:,1] == 27.1))

class TestTeamLengthWidth(unittest.TestCase):
    """Unit test class for the get_team_length_and_width function.
    """

    def test_correct_width(self):
        testData = np.ones((10,22))
        testData[:,0::2] = 15.0
        testData[np.arange(10), np.arange(0, 20, 2)] = np.arange(10) * 10.0
        test_x = np.array([15., 5., 5., 15., 25., 35., 45., 55., 65., 75.])

        res = gr.get_team_length_and_width(testData)
        self.assertTrue(np.all(res[:,0] == test_x))

    def test_length(self):
        testData = np.ones((10,22))
        testData[:,1::2] = 15.0
        testData[np.arange(10), np.arange(1, 20, 2)] = np.arange(10) * 10.0
        test_y = np.array([15., 5., 5., 15., 25., 35., 45., 55., 65., 75.])

        res = gr.get_team_length_and_width(testData)
        self.assertTrue(np.all(res[:,1] == test_y))

class TestTeamSurface(unittest.TestCase):
    """Unit test class for the get_team_surface function.
    """

    def test_correct_area(self):
        testData = np.random.rand(10,22)
        testData[:, :2] = (-2, 2)
        testData[:, 2:4] = (-2, -2)
        testData[:, 4:6] = (2, 2)
        testData[:, 6:8] = (2, -2)
        res = gr.get_team_surface(testData)
        self.assertTrue(np.all(res == 16))

class TestStretchIndex(unittest.TestCase):
    """Unit test class for the stretch_index function.
    """
    def setUp(self):
        self.no_frames = 10
        arr = np.array([[1.0, 1.0, 3.0, 1.0, 1.0, 3.0, 3.0, 3.0]])
        self.testData = np.repeat(arr, 10, axis=0)

    def test_correct_shape(self):
        res = gr.get_stretch_index(self.testData)
        self.assertTrue(np.all(res.shape == (self.no_frames, 1)))

    def test_correct_SI(self):
        res = gr.get_stretch_index(self.testData)
        self.assertTrue(np.all(res == np.sqrt(2.0)))

class TestTeamRanges(unittest.TestCase):
    """Unit test class for the get_team_ranges function.
    """

    def setUp(self):
        self.no_players = 5
        self.no_frames = 10
        arr = np.ones((self.no_frames, self.no_players * 2))
        arr[0, :] = 10.0
        arr[1, :] = 3.0
        arr[2, :] = 10.0
        self.testData = arr
        self.res = gr.get_team_ranges(self.testData)
    
    def test_correct_shape(self):
        self.assertTrue(np.all(self.res.shape == (self.no_players, 4)))

    def test_correct_midpoint(self):
        test_val = np.mean(self.testData[:,1])
        self.assertTrue(np.all(self.res[:,:2] == test_val))

    def test_correct_std(self):
        test_val = np.std(self.testData[:,1])
        self.assertTrue(np.all(self.res[:,2:] == test_val))
