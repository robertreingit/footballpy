# -*- coding: utf-8 -*-
"""

@author: rein
@license: MIT
@version: 0.1
"""

from __future__ import print_function
import unittest
import footballpy.analytics.pitch_space as ps
import numpy as np

class TestPitchGridFunctions(unittest.TestCase):
    """Unit test class for the pitch grid functions.
    """

    @classmethod
    def setUpClass(cls):
        cls._grid, cls._grid_cell_area = ps.create_pitch_grid((4,2), 1.0)

    def test_correct_grid_pts(self):
        testData = np.zeros((8,2))
        testData[:4,1] = .5
        testData[4:,1] = 1.5
        testData[:,0] = np.tile(np.arange(.5, 3.6, 1.0), 2)
        self.assertTrue(np.all(self._grid == testData))

    def test_grid_size(self):
        self.assertTrue(self._grid_cell_area == 1.0)

    def test_correct_assignment(self):
        testData = np.array([0,1,1,2,0,1,1,2,1,2,2,0,1,2,2,0])
        testData.shape = (2,8)
        players = np.array(
            [[[.2, .2], [2.0, 1.0],[3.2, 1.2]],
            [[3.3, 0.9], [.3, .3],[2.1, 1.1]]])
        winner = ps.assign_grid_pts_to_players(self._grid, players)
        self.assertTrue(np.all(winner == testData.transpose()))

    def test_correct_mask(self):
        testData = np.array([[1.5, 1.5], [2.5, 1.5], [3.5, 1.5]])
        grid_clipped, mask = ps.clip_pitch_grid(self._grid, 1.0, 1.0)
        self.assertTrue(np.all(testData == grid_clipped))

    def test_correct_player_space(self):
        testData = [[0.0], [2.0], [28.0]]
        grid, cell_area = ps.create_pitch_grid((10, 3), 1)
        players = np.array(
            [[[.1, .1], [.3, .3], [2.1, 1.1]]])
        winner = ps.assign_grid_pts_to_players(grid, players)
        assignment = ps.calculate_pitch_space_per_player(winner, 3, cell_area)
        self.assertTrue(np.all(testData == assignment))
