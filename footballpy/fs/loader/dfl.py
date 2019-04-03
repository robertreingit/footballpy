# -*- coding: utf-8 -*-
"""
dfl: Module which provides parsing function for Soccer
            position data. Individual parsers are provided for
            general match information data, match event data,
            and match position data.

@author: rein
@license: MIT
@version 0.1
"""

from __future__ import print_function
from xml.sax import make_parser, ContentHandler
from xml.sax.handler import feature_external_ges
import datetime as dt
import dateutil.parser as dup
import numpy as np

class MatchInformationParser(ContentHandler):
    """A XML parser for DFL match information files.
    
    Pulls out the pitch dimensions, and player information.
    Args:
    Returns:
    """

    def __init__(self):
        """Initialization of attributes."""
        ContentHandler.__init__(self)
        self.inTeam = False
        self.inHomeTeam = False
        self.teams = {'home': [], 'guest': [] }
        self.match = {'stadium': {'length': 0, 'width': 0 },
                      'home':'', 'guest':''}

    def startElement(self,name,attrs):
        """Gets called for every starting tag."""

        if name == "Environment":
            self.match['stadium']['length'] = float(attrs['PitchX'])
            self.match['stadium']['width'] = float(attrs['PitchY'])

        elif name == "Team":
            self.inTeam = True
            role = attrs['Role']
            teamID = attrs['TeamId']
            color = attrs['PlayerMainColorOfShirt']
            if role == "home":
                self.inHomeTeam = True
                self.match['home'] = teamID
                self.match['team_color_home'] = color
            elif role == "guest":
                self.inHomeTeam = False
                self.match['guest'] = teamID
                self.match['team_color_guest'] = color
            else:
                raise NameError("Couldn't determine role")

        elif name == "Player" and self.inTeam:
            name = attrs['Shortname']
            pid = attrs['PersonId']
            trikot = int(attrs['ShirtNumber'])
            position = (attrs['PlayingPosition'] if 
                        'PlayingPosition' in attrs.getNames() else 
                        'NA')
            player = {"id": pid, "name":name, \
                    "trikot":trikot,"position":position}
            if self.inHomeTeam:
                self.teams['home'].append(player)
            else:
                self.teams['guest'].append(player)

        elif name == 'General':
            # get game name
            game_name_index = ('MatchTitle' if 'MatchTitle' in
                    attrs.keys() else 'GameTitle')
            game_name = attrs[game_name_index]
            self.game_name = game_name
            self.match_day = attrs['MatchDay']
            if 'Competition' in attrs.keys():
                self.match['league'] = attrs['Competition']
            elif 'CompetitionName' in attrs.keys():
                self.match['league'] = attrs['CompetitionName']
            else:
                self.match['leagu'] = 'BL_I_guess'
            self.match['season'] = attrs['Season']
            self.match['team_name_home'] = attrs['HomeTeamName']
            self.match['team_name_guest'] = attrs['AwayTeamName']
            self.match['tracking_source'] = 'dfl'
            self.match['start_date'] = dup.parse(attrs['KickoffTime'])

    def endElement(self,name):
        """Gets called for every closing tag."""
        if name == "Team":
            self.inTeam = False

    def build_result_structure(self):
        self.match['game_name'] = self.game_name
        self.match['match_day'] = self.match_day
    
    def getTeamInformation(self):
        """Extractor function."""
        self.build_result_structure()
        return self.teams, self.match
    
    def run(self,fname):
        """Runs the parse on fname."""
        parser = make_parser()
        parser.setContentHandler(self)
        parser.parse(fname)
        print('finished parsing match information')


def convertTime(tstring):
    """Converts time stamps into datetimes.
    
        convertTime converts the time string into a datetime.datetime
        object with added timezone information.
        
        Args:
            tstring: timestamp string
        Returns:
            A datetime object representing the timestamp.
    """    
    return dup.parse(tstring) 


class Substitution:
    """
    A simple wrapper object for substitution events.
    """
    def __init__(self, time, teamID, pin, pout, position, hid = None):
        self.time = time
        self.teamID = teamID
        self.pin = pin
        self.pout = pout
        self.position = position
        self.halftime = hid

    def update_halftime(self, play_time):
        """Updates the halftime index.

            Args:
            Returns:
        """
        if self.time > play_time['secondHalf'][0]: 
            self.halftime = 2
        else:
            self.halftime = 1
    
    def __repr__(self):
        return ('%s: %s= ->%s - %s->, %s' %  
            (self.time, self.teamID, self.pin, self.pout, self.position))


class MatchEventParser(ContentHandler):
    """
    Parses the event data for substitutions.
    """
    def __init__(self):
        ContentHandler.__init__(self)
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
            sub = Substitution(stime, teamID, pin, pout, position)
            self.subs.append(sub)            
        elif name == "KickoffWhistle":
            section = attrs['GameSection']
            self.playing_time[section][0] = convertTime(self.eventTime)
        elif name == "FinalWhistle":
            section = attrs['GameSection']
            self.playing_time[section][1] = convertTime(self.eventTime)
    
    def run(self,fname):
        parser = make_parser()
        parser.setContentHandler(self)
        parser.parse(fname)
        print('finished parsing event data')
    
    def getEventInformation(self):
        return self.playing_time, self.subs


def get_match_events(match_event_file):
    """Function to parse dfl match events.

        Args:
            match_event_file: full path to match event file.
        Returns:
            a dictionary with event entries.
    """
    from lxml import etree

    def prepend_name_to_itemlist(name, item_lst):
        """Prepends a name to items"""
        return [(name + item[0], item[1]) for item in item_lst]
    
    def process_goal_shot(shot):
        """Small formatter for goal shots:
            Args:
            Returns:
        """
        event_entries = shot.xpath('./ancestor::Event')[0].items()
        shot_entries = shot.items()
        result_entries = prepend_name_to_itemlist('Result:', shot.getchildren()[0].items())
        result_type = [('ResultType', shot.getchildren()[0].tag)]
        shot_dict = dict(event_entries + shot_entries + result_entries + result_type)
        shot_dict['EventTime'] = dup.parse(shot_dict['EventTime'])
        return shot_dict

    result = dict()

    root = etree.parse(match_event_file).getroot()
    result['goal_shots'] = [process_goal_shot(shot) for shot in root.xpath('//ShotAtGoal')]
    return result


def calculate_frame_estimate(playing_time,padding_time = 5*60, freq = 25):
    secs_1st = (playing_time['firstHalf'][1] - playing_time['firstHalf'][0]).seconds
    secs_2nd = (playing_time['secondHalf'][1] - playing_time['secondHalf'][0]).seconds
    no_frames = (secs_1st + secs_2nd + padding_time) * freq
    return int(no_frames)

        
class MatchPositionParser(ContentHandler):
    """
    A parser for the position data.
    Attributes:
        currentID
        currentPos
        timeStamps
        tmpTimeStamp
        inFrameSet
        teamID
        gameSection
        isBall
        positionData
        ball
        match
        teams
    """
    def __init__(self,match,teams,no_frames = 200000):
        ContentHandler.__init__(self)
        self.currentID = ""
        self.currentPos = np.zeros((no_frames,6),dtype='float32')
        self.timeStamps = [[],[]]
        self.tmpTimeStamp = []
        self.inFrameSet = False
        self.frameCounter = 0
        self.teamID = ""
        self.gameSection = ""
        self.isBall = False
        self.position_data = {'home': {'1st':[], '2nd':[]},
                          'guest': {'1st':[], '2nd':[]}}
        self.ball = [0]*2
        self.match = match
        self.teams = teams

    def startElement(self,name,attrs):
        if name == "FrameSet":
            self.inFrameSet = True
            self.frameCounter = 0
            self.currentID = attrs['PersonId']
            self.gameSection = attrs["GameSection"]
            self.teamID = attrs['TeamId']
            if self.teamID.upper() == "BALL":
                self.isBall = True
                print("Ball")
            print(self.currentID)
        elif (name == "Frame") & self.inFrameSet:
            x = float(attrs['X'])
            y = float(attrs['Y'])
            frame = float(attrs['N'])
            if not self.isBall:
                self.currentPos[self.frameCounter,:3] = (frame,x,y)
            else: # ball data
                z = float(attrs['Z'])
                possession = float(attrs['BallPossession'])
                ball_status = float(attrs['BallStatus'])
                self.currentPos[self.frameCounter,] = ( 
                    frame,x,y,z,possession,ball_status)
                # add timestamp information
                timestamp = convertTime(attrs['T'])
                self.tmpTimeStamp.append(timestamp)

            self.frameCounter += 1

    def endElement(self,name):
        if name == "FrameSet":
            print("Processed %d frames" % (self.frameCounter))
            self.inFrameSet = False
            # get team: A or B            
            section = self.gameSection
            teamID = self.teamID
            if self.isBall: # ball data
                if section == "firstHalf":
                    self.ball[0] = np.copy(
                            self.currentPos[:self.frameCounter,])
                    self.timeStamps[0] = self.tmpTimeStamp

                elif section == "secondHalf":
                    self.ball[1] = np.copy(
                            self.currentPos[:self.frameCounter,])
                    self.timeStamps[1] = self.tmpTimeStamp
                else:
                    raise LookupError
                self.tmpTimeStamp = []

            else: # player data
                secID = '1st' if section == 'firstHalf' else '2nd'
                teamRole = 'home' if teamID == self.match['home'] else 'guest'
                play_pos = (self.teams[teamRole][[p['id'] for p in 
                    self.teams[teamRole]].index(self.currentID)]['position'])
                entry = (self.currentID,np.copy(self.currentPos[:self.frameCounter,:3]),play_pos)
                self.position_data[teamRole][secID].append(entry)
            # cleaning up
            self.gameSection = "NaN"
            self.frameCounter = 0
            self.teamID = ''
            if self.isBall:                
                self.isBall = False

    def run(self,fname):
        """Starts parsing fname.

        Args:
            fname is the name of the file.
        Returns:
            Nothing
        """
        parser = make_parser()
        parser.setContentHandler(self)
        print('Start parsing position data')
        parser.parse(fname)
        print('finished parsing position data')


    def getPositionInformation(self):
        """Extractor function to retrieve position data.
        Args:
            None
        Returns:
            The player position data and the ball data.
        """
        return self.position_data, self.ball, self.timeStamps

def correct_substitions():
    """Correct position data overlap during substitions.

        Args:
        Returns:
    """
    pass

def get_df_from_files(match_info_file, match_pos_file):
    """Wrapper function to get a pandas dataframe from DFl position data. 

    This function is meant as an outside API to load position data from
    DFL files.

    Args:
        match_info_file: full path to the MatchInformation file.
        match_pos_file: full path to the PositionData file.
    Returns:
        A tuple with a Pandas dataframe with the position data,
        the teams information dictionary, and
        the match information dictionary
    """
    import footballpy.fs.loader.papi as papi

    mip = MatchInformationParser()
    mip.run(match_info_file)
    teams, match = mip.getTeamInformation()

    mpp = MatchPositionParser(match, teams)
    mpp.run(match_pos_file)
    pos_data, ball_data, timestamps = mpp.getPositionInformation()
    pos_df = papi.pos_data_to_df(pos_data, ball_data)
    timestamps_concatenated = timestamps[0] + timestamps[1]
    assert(len(timestamps_concatenated) == pos_df.shape[0])
    pos_df['time'] = timestamps_concatenated
    return pos_df, teams, match

def get_match_info(match_info_file):
    """Extracts match information data.

        Args:
            match_info_file: full path to vistrack-matchfacts file.
        Returns:
            a match information dictionary.
    """
    from lxml import etree

    root = etree.parse(match_info_file).getroot()
    match = dict()
    general_element = root.xpath('//MatchInformation/General')[0]
    match['game_name'] = general_element.get('GameTitle')
    match['match_id'] = general_element.get('MatchId')
    match['match_day'] = general_element.get('MatchDay')
    match['team_name_home'] = general_element.get('HomeTeamName')
    match['team_name_away'] = general_element.get('AwayTeamName')
    match['home'] = general_element.get('HomeTeamId')
    match['away'] = general_element.get('AwayTeamId')
    match['tracking_source'] = 'DFL'
    match['start_date'] = dup.parse(general_element.get('KickoffTime'))
    match['season'] = general_element.get('Season')
    match['league'] = general_element.get('Competition')
    match['team_color_home'] = root.xpath('//Teams/Team[@Role="home"]/@PlayerMainColorOfShirt')[0]
    match['team_color_away'] = root.xpath('//Teams/Team[@Role="guest"]/@PlayerMainColorOfShirt')[0]
    stadium = dict()
    stadium['width'] = general_element.get('PitchY')
    stadium['length'] = general_element.get('PitchX')
    match['stadium'] = stadium
    return match

def get_team_info(match_info_file):
    """Caculates the team information from matchfacts file.
        Args:
            match_info_file: full path to the vistrack-matchfacts file
        Returns:
            a dictionary with the team lists
    """
    from lxml import etree

    def process_player(element):
        """
        """
        player_items = dict(element.items())
        player = dict()
        player['id'] = player_items['PersonId']
        player['name'] = player_items['FirstName'] + ' ' + player_items['LastName']
        player['trikot'] = player_items['ShirtNumber']
        player['position'] = player_items['PlayingPosition'] if 'PlayingPosition' in player_items else ''
        return player

    root = etree.parse(match_info_file).getroot()
    team = dict()
    team['home'] = [process_player(player) for player in root.xpath('//Teams/Team[@Role="home"]/Players/Player')]
    team['away'] = [process_player(player) for player in root.xpath('//Teams/Team[@Role="guest"]/Players/Player')]
    return team


#######################################
if __name__ == "__main__":
    
    print("Parsing match information")
    mip = MatchInformationParser()
    mip.run(match_info_file)
    teams, match = mip.getTeamInformation()
    
    """
    
    print("Parsing event data")
    mep = MatchEventParser()
    fname_info = data_path + "EventData/" + fname
    mep.run(fname_info)
    play_time, subs = mep.getEventInformation()
    """
    
    print("Parsing position data")
    mpp = MatchPositionParser(match,teams)
    mpp.run(match_pos_file)
    #pos_data,ball_data,timestamps = mpp.getPositionInformation()
    df, teams, match = get_df_from_files(match_info_file, match_pos_file)
