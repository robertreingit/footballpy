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
        self.line = '10008,1,1,2020-12-12T14:30:48.680+02:00,1,22;#p67359,-18.49,5.60,9.91;p66579,-6.46,28.93,8.64;p96615,-20.18,-1.90,5.61;p160541,-12.25,24.26,1.53;p166028,-1.82,5.61,5.16;p27542,-42.81,2.25,0.66;p95754,0.93,25.15,10.01;p51955,-1.73,28.34,7.62;p110927,-14.14,26.23,14.29;p17351,1.78,0.40,6.04;p165687,-10.26,19.54,4.17;p9893,33.50,4.45,6.05;p62378,-7.69,27.07,2.00;p62490,-12.50,3.25,6.00;p156787,-6.70,24.53,9.11;p162296,-12.62,25.77,0.37;o44472,9.95,-34.24,5.18;p180839,-21.25,6.65,7.54;o43113,-23.33,34.76,4.71;p95609,3.42,11.78,8.46;p70017,-12.50,13.65,5.24;p168083,-17.05,-2.09,7.89;p51978,-21.80,17.26,4.53;p20384,-3.97,12.42,5.70;o41441,-7.53,17.51,6.62;#10.01,11.02,12.12,17.04,0,2;'

    def test_ball_data(self):
        res = sp.process_line(self.line) 
        self.assertEqual(res[0], 10008)
        self.assertEqual(res[1], 10.01)
        self.assertEqual(res[2], 11.02) 
        self.assertEqual(res[3], 12.12) 
