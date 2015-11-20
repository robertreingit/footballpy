# -*- coding: utf-8 -*-
"""
test_impire_parser: unittests for the impire_parser_functions

The tests relies on the specific test files which are pruned
versions of original files.

@author: rein
@license: MIT
@version 0.1
"""

import unittest
import numpy as np
import impire_parser

class TestMatchPosition(unittest.TestCase):
    """Unit test class for the MatchPositionParser.
    """
    @classmethod
    def setUpClass(cls):
        cls.pos_file = 'test/impire/123456.pos'
        cls.match_file = 'test/impire/vistrack-matchfacts-123456.xml'

    def test_read_in_position(self):
        """Asserts basic read-in functionality."""
        home,tmp2,tmp2,tmp3 = impire_parser.read_in_position_data(TestMatchPosition.pos_file)
        self.assertTrue(home.shape == (7,11,3))

    def test_half_time_index(self):
        """Checks whether the half-time index is properly extracted."""
        tmp1,tmp2,tmp3,ht = impire_parser.read_in_position_data(TestMatchPosition.pos_file)
        self.assertTrue(np.all(ht[:4] == 1))
        self.assertTrue(np.all(ht[4:] == 2))

    def test_half_time_split(self):
        """Tests the splitting of the position data into two halves."""
        home,tmp2,tmp3,ht = impire_parser.read_in_position_data(TestMatchPosition.pos_file)
        home_1,home_2 = impire_parser.split_positions_into_game_halves(home,ht)
        self.assertTrue(home_1.shape == (4,11,3))
        self.assertTrue(home_2.shape == (3,11,3))

    def test_sort_raw_data(self):
        """Tests whether the raw data is sorted properly."""
        home,tmp,tmp2,tmp3 = impire_parser.read_in_position_data(TestMatchPosition.pos_file)
        home_s = impire_parser.sort_position_data(home)
        test_array = np.arange(7) + 1.0
        target_array = [d for d in home_s if np.all(d[:,0]==15.0)][0][:,1]
        self.assertTrue(np.all(target_array == test_array))

    def test_sort_raw_data2(self):
        """Tests sequence of raw data."""
        data = impire_parser.read_in_position_data(TestMatchPosition.pos_file)
        home_s = impire_parser.sort_position_data(data[0])
        self.assertTrue(home_s[9][0,1] == -11.0)

    def test_split_and_sort(self):
        """Test processing chain after sorting."""
        home,tmp2,tmp3,ht = impire_parser.read_in_position_data(TestMatchPosition.pos_file)
        home_1,home_2 = impire_parser.split_positions_into_game_halves(home,ht)
        home_1s = impire_parser.sort_position_data(home_1)
        test_data = next(p for p in home_1s if p[0,0] == 2)
        self.assertTrue(np.all(test_data[:,0] == 2.0))
        self.assertTrue(test_data[0,1] == -11.9269)

    def test_team_load(self):
        """Tests teams loading."""
        mip = impire_parser.MatchInformationParser()
        mip.run(TestMatchPosition.match_file)
        teams, match = mip.getTeamInformation()
        self.assertTrue(len(teams['home']) == 18)
        self.assertTrue(len(teams['guest']) == 18)
        self.assertTrue(len([p for p in teams['home'] if p['id'] == '10000']) == 1)
        self.assertTrue((next(p for p in teams['guest'] if p['id'] == '11003')
            ['name'] == 'Cliegg Lars'))

    def test_stadium_specs(self):
        """Tests whether the stadium specs load function works"""
        stadium = impire_parser.read_stadium_dimensions_from_pos(TestMatchPosition.pos_file)
        self.assertEqual(stadium, {'length':105.0, 'width':68.0})



if __name__ == '__main__':
    unittest.main()
    
