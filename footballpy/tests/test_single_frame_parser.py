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

class TestProcessLine(unittest.TestCase):
    """Unit tests for the process_line function.
    """

    def setUp(self):
        self.line = '10008,1,1,2020-12-12T14:30:48.680+02:00,1,22;#p1,-18.49,5.60,9.91;p2,-6.46,28.93,8.64;p3,-20.18,-1.90,5.61;p4,-12.25,24.26,1.53;p5,-1.82,5.61,5.16;p6,-42.81,2.25,0.66;p7,0.93,25.15,10.01;p8,-1.73,28.34,7.62;p9,-14.14,26.23,14.29;p10,1.78,0.40,6.04;p11,-10.26,19.54,4.17;p21,33.50,4.45,6.05;p22,-7.69,27.07,2.00;p23,-12.50,3.25,6.00;p24,-6.70,24.53,9.11;p25,-12.62,25.77,0.37;o44472,9.95,-34.24,5.18;p26,-21.25,6.65,7.54;o43113,-23.33,34.76,4.71;p27,3.42,11.78,8.46;p28,-12.50,13.65,5.24;p29,-17.05,-2.09,7.89;p30,-21.80,17.26,4.53;p31,-3.97,12.42,5.70;o44444,-7.53,17.51,6.62;#10.01,11.02,12.12,17.04,0,2;'

    def test_ball_data(self):
        res = sp.process_line(self.line) 
        ball = res['ball']
        self.assertEqual(ball[0], 10008)
        self.assertEqual(ball[1], 10.01)
        self.assertEqual(ball[2], 11.02) 

    def test_player_data(self):
        res = sp.process_line(self.line)
        players = {x: res[x] for x in res if x not in {'ball'}}
        self.assertEqual(len(players), 22)
        test_keys = ({'p' + str(i) for i in range(1,12)} |
                {'p' + str(i) for i in range(21,32)})
        self.assertTrue(test_keys == set(players.keys()))
        self.assertEqual(players['p1'], (10008, -18.49, 5.60))
        self.assertEqual(players['p2'], (10008, -6.46, 28.93))
        self.assertEqual(players['p3'], (10008, -20.18, -1.90))
        self.assertEqual(players['p21'], (10008, 33.50, 4.45))
        self.assertEqual(players['p26'], (10008, -21.25, 6.65))

class TestGetDataFiles(unittest.TestCase):
    """Unit tests for the get_data_folder function.
    """

    def test_file_count(self):
        test_folder = 'footballpy/testfiles/single/'
        (res_files, res_frames) = sp.get_data_files(test_folder)
        self.assertEqual(len(res_files), 2)

