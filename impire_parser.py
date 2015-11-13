# -*- coding: utf-8 -*-
"""
impire_parser : Module which provides parsing function for Soccer
            position data based on the impire format.
        Individual parsers are provided for
            general match information data, match event data,
            and match position data.

@author: rein
@license: MIT
@version 0.1
"""
import xml.sax, xml.sax.handler
import datetime as dt
import dateutil.parser as dup
import numpy as np
import pdb

def read_stadium_specs():
    """Reads the stadium width and lenght from a csv file."""
    stadium_specs = '../data/game_stadium_keys.csv'
    fid = open(stadium_specs)
    header = fid.readline().rstrip().split(';')
    entries = [[] for x in range(len(header))]
    stadium_specs = [game.rstrip() for game in fid.readlines()]
    for game in stadium_specs:
        for (idx,entry) in enumerate(game.split(';')):
            entries[idx].append(entry)
    specs = dict(zip(header,entries))
    return specs 

def add_stadium_information(match,specs):
    """ Adds stadium width and the length to match data

    Args:
    Returns:
    """
    id_game = specs['event_key'].index(match['match-id'])
    if id_game < 0:
        raise LookupError("Couldn't find match")
    stadium = {'length': specs['Length'][id_game],
            'width': specs['Width'][id_game]}
    match['stadium'] = stadium

class MatchInformationParser(xml.sax.handler.ContentHandler):
    """A XML parser for DFL match information files.
    
    Pulls out the pitch dimensions, and player information.
    Args:
    """

    def __init__(self):
        """Initialization of attributes."""
        self.inTeam = False
        self.inHomeTeam = False
        self.inPlayer = False
        self.currentPlayer = None
        self.teams = {'home': [], 'guest': [] }
        self.match = {'match-id': 0, 'home':'', 'guest':''}

    def startElement(self,name,attrs):
        """Gets called for every starting tag."""

        if name == 'event-metadata':
            self.match['match-id'] = attrs['event-key']

        elif name == "team":
            self.inTeam = True

        elif name=='team-metadata' and self.inTeam:
            role = attrs['alignment']
            teamID = attrs['team-key']
            if role == "home":
                self.inHomeTeam = True
                self.match['home'] = teamID
            elif role == "away":
                self.inHomeTeam = False
                self.match['guest'] = teamID
            else:
                raise NameError("Couldn't determine role")
        elif name == 'player':
            self.inPlayer = True

        elif name == "player-metadata" and self.inTeam:
            pid = attrs['player-key']
            trikot = int(attrs['uniform-number'])
            if 'position-event' in attrs.getNames():
                position = attrs['position-event']
            else:
                position = attrs['position-regular']
            self.currentPlayer = {
                        "id": pid,
                        "trikot": trikot,
                        "position": position
                    }

        elif name == 'name' and self.inPlayer:
            name = attrs['nickname']
            self.currentPlayer['name'] = name
            if self.inHomeTeam:
                self.teams['home'].append(self.currentPlayer.copy())
            else:
                self.teams['guest'].append(self.currentPlayer.copy())
            self.currentPlayer = None

    def endElement(self,name):
        """Gets called for every closing tag."""
        if name == "team":
            self.inTeam = False
        elif name == 'player':
            self.inPlayer = False
    
    def getTeamInformation(self):
        """Extractor function."""
        return self.teams, self.match
    
    def run(self,fname):
        """Runs the parse on fname."""
        parser = xml.sax.make_parser()
        parser.setContentHandler(self)
        parser.parse(fname)
        print 'finished parsing match information'


def convertTime(tstring):
    """ Converts time stamps into datetimes.
    
    convertTime converts the time string into a datetime.datetime
    object with added timezone information.
    
    Args:
        tstring: timestamp string
    Returns:
        A datetime object representing the timestamp.
    """    
    return dup.parse(tstring) 



class MatchEventParser(xml.sax.handler.ContentHandler):
    """
    Parses the event data for substitutions.
    """
    def __init__(self):
        self.eventTime = ""
        self.playing_time = { 
                "firstHalf": ["",""], "secondHalf": ["",""] }
        self.subs = []
        
    def startElement(self,name,attrs):
        if name == "Event":
            self.eventTime = attrs["EventTime"]
        elif name == "Substitution":
            teamID = attrs['Team']
            pin = attrs['PlayerIn']
            pout = attrs['PlayerOut']
            position = attrs['PlayingPosition']
            stime = convertTime(self.eventTime)
            sub = Substitution(stime,teamID,pin,pout,position)
            self.subs.append(sub)            
        elif name == "KickoffWhistle":
            section = attrs['GameSection']
            self.playing_time[section][0] = convertTime(
                    self.eventTime)
        elif name == "FinalWhistle":
            section = attrs['GameSection']
            self.playing_time[section][1] = convertTime(self.eventTime)
    
    def run(self,fname):
        parser = xml.sax.make_parser()
        parser.setContentHandler(self)
        parser.parse(fname)
        print 'finished parsing event data'
    
    def getEventInformation(self):
        return self.playing_time, self.subs
        
def calculate_frame_estimate(playing_time,padding_time = 5*60, freq = 25):
    secs_1st = (playing_time['firstHalf'][1] - playing_time['firstHalf'][0]).seconds
    secs_2nd = (playing_time['secondHalf'][1] - playing_time['secondHalf'][0]).seconds
    no_frames = (secs_1st + secs_2nd + padding_time) * freq
    return int(no_frames)

        
def read_in_position_data(fname):
    """Reads in a pos file and extract the ball/player data
    Args:
    Returns:
    """

    # MAGIC NUMBER
    _MISSING_ = -10000.0
    NO_PLAYER = 11
    NO_DIM = 3      # FRAME, X, Z
    NO_DIM_BALL = 6     # FRAME, X, Y, Z, POSSESSION, STATUS

    no_frames = sum([1 for f in open(fname)])

    home_team = np.ones((NO_PLAYER,no_frames,NO_DIM)) * _MISSING_
    guest_team = home_team.copy()
    ball = np.ones((no_frames,6)) * _MISSING_

    for i,frame in enumerate(open(fname)):
        #0: Frame, 1: Home, 2: Guest, 3: Referee, 4: Ball
        hash_split = frame.split('#')
        # get frame index
        frame = int(hash_split[0][:-1].split(',')[0])
        # process home team
        for j,player in enumerate(hash_split[1][:-1].split(';')):
            player_data = player.split(',')
            player_id = int(player_data[0])
            player_x = float(player_data[1])
            player_y = float(player_data[2])
            home_team[j,i,:] = [player_id, player_x, player_y]

    return home_team

def sort_position_data(pos):
    """Sorts the position data according to player and period.
    """
    # TODO


#######################################
if __name__ == "__main__":
    
    data_path = "../data/2011-12 BL 14.Sp. Augsburg vs. Wolfsburg/"
    fname = 'test.xml'
    stadium_specs = read_stadium_specs()
    
    print "Parsing match information"
    mip = MatchInformationParser()
    fname_match = data_path + 'vistrack-actions-130330.xml'
    mip.run(fname_match)
    teams, match = mip.getTeamInformation()
    
    home = read_in_position_data('test/impire/123456_test.pos')
    """
    print "Parsing event data"
    mep = MatchEventParser()
    fname_info = data_path + "EventData/" + fname
    mep.run(fname_info)
    play_time, subs = mep.getEventInformation()
    
    print "Parsing position data"
    mpp = MatchPositionParser(match,teams)
    fname_pos = data_path + "/ObservedPositionalData/" + fname
    mpp.run(fname_pos)
    pos_data,ball_data,timestamps = mpp.getPositionInformation()
    """ 
