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

class TestsRescaleMatrix(unittest.TestCase):
    """Unit test class for the rescale_global_matrix function.
    """
    def test_rescaling(self):
        test_case = np.ones((10,26))
        test_case[:,:4] = -13.0
        test_specs = { 'length': 4.0, 'width': 6.0 }
        res = fq.rescale_global_matrix(test_case, test_specs)
        # Testing meta-data untouched
        self.assertTrue(np.all(np.all(res[:,:4] == -13.0)))
        # Testing scaling
        self.assertTrue(np.all(np.all(res[:,4::2] == 2.0)))
        self.assertTrue(np.all(np.all(res[:,5::2] == 3.0)))

class TestDetermineCuttingFrames(unittest.TestCase):
    """Unit test class for the determine_cutting_frames function.
    """
    @classmethod
    def setUpClass(cls):
        cls.__testdata = np.ones((50, 26))

    def test_half_time(self):
        """
        """
        testMatrix = TestDetermineCuttingFrames.__testdata.copy()
        testMatrix[25:, 3] = 2
        res = fq.determine_cutting_frames(testMatrix)
        self.assertTrue(np.all((0, 25, 49) == res))

    def test_possession(self):
        """
        """
        testMatrix = TestDetermineCuttingFrames.__testdata.copy()
        testMatrix[:, 1] = 0.0
        testMatrix[5:10, 1] = 1
        testMatrix[22:27, 1] = 1
        res = fq.determine_cutting_frames(testMatrix)
        test_vector = np.array([0, 5, 10, 22, 27, 49])
        self.assertTrue(np.all(test_vector == res))

class TestSegmentPositionData(unittest.TestCase):
    """Unit test class for the segment_position_data function.
    """

    @classmethod
    def setUpClass(cls):
        test_cutting_pts = (0, 10, 12, 19, 25, 45)
        test_array = np.ones((45,3))
        test_array[10:12,:] = 2.0
        test_array[12:19,:] = 3.0
        test_array[19:25,:] = 4.0
        test_array[25:,:] = 5.0
        cls.__pos_data = test_array
        cls.__cut_pts = test_cutting_pts

    def test_segmentation_length(self):
        res = fq.segment_position_data(
                TestSegmentPositionData.__pos_data,
                TestSegmentPositionData.__cut_pts)
        self.assertEqual(len(res), len(TestSegmentPositionData.__cut_pts)-3)

    def test_segmentation_content(self):
        res = fq.segment_position_data(
            TestSegmentPositionData.__pos_data,
            TestSegmentPositionData.__cut_pts)
        for i, segment in enumerate(res):
            self.assertTrue(np.all(np.all(segment == i+2.0)))
