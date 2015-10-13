# -*- coding: utf-8 -*-
"""
test_dfl_parser: unittests for the dfl_parser_functions

The tests relies on the specific test files which are pruned
versions of original files.

@author: rein
@license: MIT
@version 0.1
"""

import unittest
import dfl_parser
from datetime import datetime
import dateutil.parser as dup
import numpy as np

class TestMatchInformation(unittest.TestCase):
    """Unit test class for the dfl_parser
    """
    @classmethod
    def setUpClass(cls, fname='./test/dfl/MatchInformation/test.xml'):
        mip = dfl_parser.MatchInformationParser()
        mip.run(fname)
        cls._teams,cls._match = mip.getTeamInformation()

    def test_pitch_specs(self):
        match = TestMatchInformation._match
        self.assertEqual(match['stadium']['length'],105.0)
        self.assertEqual(match['stadium']['width'],69.0);

    def test_team_ids(self):
        match = TestMatchInformation._match
        self.assertEqual(match['home'],'DFL-ABC-12345A')
        self.assertEqual(match['guest'],'DFL-ABC-12345B')

    def test_no_players(self):
        teams = TestMatchInformation._teams
        self.assertEqual(len(teams['guest']),6)
        self.assertEqual(len(teams['home']),6)

    def test_player_name(self):
        teams = TestMatchInformation._teams
        self.assertEqual(teams['home'][0]['id'], u"DFL-OBJ-a00001")

    def test_single_player(self):
        teams = TestMatchInformation._teams
        barney = [p for p in teams['guest'] if \
                    p['id'] == 'DFL-OBJ-b00004'][0]
        self.assertEqual(barney['name'],'B. Rubble')
        self.assertEqual(barney['position'], 'MZ')
        self.assertEqual(barney['trikot'],4)

class TestMatchEvent(unittest.TestCase):
    """Unit test class for the MatchEventParser.
    """
    @classmethod
    def setUpClass(cls, fname='./test/dfl/EventData/test.xml'):
        mep = dfl_parser.MatchEventParser()
        mep.run(fname)
        cls._play_time, cls._subs = mep.getEventInformation()

    def test_playing_time(self):
        play_time = TestMatchEvent._play_time
        self.assertEqual(play_time['firstHalf'][0],
               dup.parse('2015-05-16T15:30:41.247+02:00'))
        self.assertEqual(play_time['firstHalf'][1],
               dup.parse('2015-05-16T16:15:44.247+02:00'))

class TestMatchPosition(unittest.TestCase):
    """Unit test class for the MatchPositionParser.
    """
    @classmethod
    def setUpClass(cls, fname='./test/dfl/ObservedPositionalData/test.xml'):
        mip = dfl_parser.MatchInformationParser()
        fname_match = "./test/dfl/MatchInformation/test.xml"
        mip.run(fname_match)
        teams, match = mip.getTeamInformation()
        mpp = dfl_parser.MatchPositionParser(match,teams)
        mpp.run(fname)
        cls._pos_data, cls._ball_data = mpp.getPositionInformation()

    def test_number_of_player(self):
        pos_data = TestMatchPosition._pos_data
        guest_1st = pos_data['guest']['1st']
        guest_2nd = pos_data['guest']['2nd']
        home_1st = pos_data['home']['1st']
        home_2nd = pos_data['home']['2nd']
        self.assertEqual(len(guest_1st),3)
        self.assertEqual(len(guest_2nd),4)
        self.assertEqual(len(home_1st),3)
        self.assertEqual(len(home_2nd),4)

    def test_xy_data(self):
        # Testing guest data
        guest_1st = TestMatchPosition._pos_data['guest']['1st']
        p_idxs = {data[0]: i for (i,data) in enumerate(guest_1st)}
        pid_1 = p_idxs[u'DFL-OBJ-b00002']
        self.assertEqual(guest_1st[pid_1][1].shape,(9,3))
        self.assertTrue(np.all(guest_1st[pid_1][1][0,:3]==(10000.0,10.0,20.0)))
        # Testing home data
        home_2nd = TestMatchPosition._pos_data['home']['2nd']
        p_idxs = {data[0]:i for (i,data) in enumerate(home_2nd)}
        pid_2 = p_idxs[u'DFL-OBJ-a00004']
        self.assertEqual(home_2nd[pid_2][1].shape,(4,3))
        self.assertTrue(np.all(home_2nd[pid_2][1][2,:2]==(100007.0,57.0)))


if __name__ == '__main__':
    unittest.main()
    
