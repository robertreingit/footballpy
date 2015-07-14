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
                datetime(2015,5,16,15,30,41,247000))
        self.assertEqual(play_time['firstHalf'][1],
                datetime(2015,5,16,16,15,44,247000))

if __name__ == '__main__':
    unittest.main()
    
