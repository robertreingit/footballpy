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
import footballpy.fs.loader.impire as impire_parser

class TestMatchPosition(unittest.TestCase):
    """Unit test class for the MatchPositionParser.
    """
    @classmethod
    def setUpClass(cls):
        cls.pos_file = './footballpy/testfiles/impire/123456.pos'
        cls.match_file = './footballpy/testfiles/impire/vistrack-matchfacts-123456.xml'

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
        home,tmp2,ball,ht = impire_parser.read_in_position_data(TestMatchPosition.pos_file)
        home_1,home_2 = impire_parser.split_positions_into_game_halves(home,ht,ball)
        self.assertTrue(home_1.shape == (4,11,4))
        self.assertTrue(home_2.shape == (3,11,4))

    def test_sort_raw_data(self):
        """Tests whether the raw data is sorted properly."""
        home,tmp,tmp2,tmp3 = impire_parser.read_in_position_data(TestMatchPosition.pos_file)
        home_s = impire_parser.sort_position_data(home,0)
        test_array = np.arange(7) + 1.0
        target_array = [d for d in home_s if np.all(d[:,0]==15.0)][0][:,1]
        self.assertTrue(np.all(target_array == test_array))

    def test_sort_raw_data2(self):
        """Tests sequence of raw data."""
        data = impire_parser.read_in_position_data(TestMatchPosition.pos_file)
        home_s = impire_parser.sort_position_data(data[0],0)
        self.assertTrue(home_s[9][0,1] == -11.0)

    def test_split_and_sort(self):
        """Test processing chain after sorting."""
        home,tmp2,ball,ht = impire_parser.read_in_position_data(TestMatchPosition.pos_file)
        home_1,home_2 = impire_parser.split_positions_into_game_halves(home,ht,ball)
        home_1s = impire_parser.sort_position_data(home_1)

        self.assertTrue(np.all(map(lambda x: x.shape == (4,4), home_1s)))
        test_data = next(p for p in home_1s if p[0,1] == 2)
        self.assertTrue(np.all(test_data[:,1] == 2.0))
        self.assertTrue(test_data[0,2] == -11.9269)

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

    def test_pos_role_combination(self):
        """Tests whether the merging of position data and role works."""
        mip = impire_parser.MatchInformationParser()
        mip.run(TestMatchPosition.match_file)
        teams, match = mip.getTeamInformation()
        home,guest,ball,half_time_id = impire_parser.read_in_position_data(TestMatchPosition.pos_file)
        home_1, home_2 = impire_parser.split_positions_into_game_halves(home,half_time_id,ball)
        home_1s = impire_parser.sort_position_data(home_1)
        pos_data_home_1 = impire_parser.combine_position_with_role(home_1s,teams['home'])
        # Han Solo is the test case: Trikot: 24, ID: 10005
        test_case = [x for x in pos_data_home_1 if x[0] == '10005'][0]
        self.assertTrue(np.all(test_case[1][2,:] == (2,-0.0825,-0.4624)))
        # Cin Drallig - Trikot: 17, ID: 11002
        guest_1, guest_2 = impire_parser.split_positions_into_game_halves(guest,half_time_id,ball)
        guest_2s = impire_parser.sort_position_data(guest_2)
        pos_data_guest_2 = impire_parser.combine_position_with_role(guest_2s, teams['guest'])
        test_case = [x for x in pos_data_guest_2 if x[0] == '11002'][0]
        self.assertTrue(np.all(test_case[1][1,:] == (37043,-0.2715,0.1733)))


if __name__ == '__main__':
    unittest.main()
    
