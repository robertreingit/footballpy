# -*- coding: utf-8 -*-
# pylint: disable=C0324
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
from xml.sax import make_parser, ContentHandler
from xml.sax.handler import feature_external_ges
import numpy as np
import dateutil.parser as dup
# import pdb

class MatchInformationParser(ContentHandler):
    """A XML parser for DFL match information files.
    
    Pulls out the pitch dimensions, and player information.
    Args:
        None
    Returns:
        None
        
    """

    def __init__(self):
        """Initialization of attributes."""
        ContentHandler.__init__(self) 
        self.inTeam = False
        self.inHomeTeam = False
        self.inPlayer = False
        self.currentPlayer = None
        self.HomeTeamName = ''
        self.GuestTeamName = ''
        self.teams = {'home': [], 'guest': [] }
        self.match = {
                'match-id': 0,
                'home':'',
                'guest':'',
                'match_day': '',
                'game_name': '',
                'start_date': '',
                'season': '',
                'league': ''}

    def startElement(self,name,attrs):
        """Gets called for every starting tag."""

        if name == 'tournament-round':
            self.match['match_day'] = attrs['round-number']

        elif name == 'tournament-metadata':
            self.match['league'] = attrs['tournament-name'].split(' ')[1]
            self.match['tracking_source'] = attrs['tournament-source'].split('.')[0]

        elif name == 'event-metadata':
            self.match['match-id'] = attrs['event-key']
            start_date = dup.parse(attrs['start-date-time'])
            self.match['start_date'] = start_date 
            if start_date.month < 8:
                self.match['season'] = '{0}/{1}'.format(start_date.year - 1, start_date.year)
            else:
                self.match['season'] = '{0}/{1}'.format(start_date.year, start_date.year + 1)

        elif name == "team":
            self.inTeam = True

        elif name == 'team-metadata' and self.inTeam:
            role = attrs['alignment']
            teamID = attrs['team-key']
            color = attrs['imp:uniform-color-hex']
            if role == "home":
                self.inHomeTeam = True
                self.match['home'] = teamID
                self.match['team_color_home'] = color
            elif role == "away":
                self.inHomeTeam = False
                self.match['guest'] = teamID
                self.match['team_color_guest'] = color
            else:
                raise NameError("Couldn't determine role")

        elif name == 'name' and self.inTeam and not self.inPlayer:
            if 'imp:dfl-3-letter-code' in attrs.keys():
                full_name = attrs['full']
                if self.inHomeTeam:
                    self.HomeTeamName = full_name
                else:
                    self.GuestTeamName = full_name

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
            self.currentPlayer['name'] = attrs['full']
            if self.inHomeTeam:
                self.teams['home'].append(self.currentPlayer.copy())
            else:
                self.teams['guest'].append(self.currentPlayer.copy())
            self.currentPlayer = None

    def endElement(self, name):
        """Gets called for every closing tag."""
        if name == "team":
            self.inTeam = False
        elif name == 'player':
            self.inPlayer = False

    def getTeamInformation(self):
        """Extractor function."""
        self.match['team_name_home'] = self.HomeTeamName
        self.match['team_name_guest'] = self.GuestTeamName
        self.match['game_name'] = self.HomeTeamName + ':' + self.GuestTeamName
        return self.teams, self.match

    def run(self, fname):
        """Runs the parse on fname."""
        print('Start reading in match information')
        parser = make_parser()
        parser.setContentHandler(self)
        # prevent external DTD load
        parser.setFeature(feature_external_ges, False)
        parser.parse(fname)
        print('finished parsing match information')

class MatchEventParser(ContentHandler):
    """XML parser for the event(action) impire data.
    """

    def __init__(self):
        """Initialization attributes."""
        ContentHandler.__init__(self) 
        self.result = dict()
        self.result['shots'] = []

    def startElement(self, name, attrs):
        """Called for every starting element encountered."""
        if name == 'action-soccer-score-attempt':
            shot = dict()
            shot['time'] = dup.parse(attrs['imp:timestamp'])
            shot['team_id'] = attrs['team-idref']
            shot['player_id'] = attrs['player-idref']
            shot['second_player_id'] = attrs['imp:second-player-idref']
            shot['attempt-method'] = attrs['score-attempt-method']
            shot['shot_result'] = attrs['score-attempt-result']
            shot['period'] = attrs['period-value']
            shot['x1'] = attrs['imp:x1']
            shot['y1']= attrs['imp:y1']
            shot['x2']= attrs['imp:x2']
            shot['y2'] = attrs['imp:y2']
            self.result['shots'].append(shot)

    def endElement(self, name):
        """Called for every closing element encoutered."""
        pass

    def run(self, match_event_file):
        """Runs the parser on the match_event_file.

            Args:
                match_event_file: full path to event file.
            Returns:
                None
        """
        parser = make_parser()
        parser.setContentHandler(self)
        parser.setFeature(feature_external_ges, False)
        parser.parse(match_event_file)

    def getEvents(self):
        """Returns the parsed data."""
        return self.result



def read_in_position_data(fname):
    """Reads in a pos file and extract the ball/player data
    Args:
		fname: name of the position data file.
    Returns:
		tuple with four entries:
		[0] = data for home team
		[1] = data for guest team
		[2] = data for ball
		[3] = half time index
    """

    print('Start reading in position data...')

    # MAGIC NUMBERS
    _MISSING_ = -10000.0
    NO_PLAYER = 11
    NO_DIM = 3      # FRAME, X, Y
    # NO_DIM_BALL = 6     # FRAME, X, Y, Z, POSSESSION, STATUS

    no_frames = sum([1 for f in open(fname)])

    home_team = np.ones((no_frames,NO_PLAYER, NO_DIM)) * _MISSING_
    guest_team = home_team.copy()
    ball = np.ones((no_frames, 6)) * _MISSING_
    half_time_id = np.ones(no_frames) * _MISSING_

    def process_player(player):
        """Extracts information from player-pos string.

            Simple routines to just split up the string.
            Args:
                player: String from pos file.
            Returns:
                Tuple with player id, x and y position.
        """
        data = player.split(',')
        pid = int(data[0])      # player identifier
        x = float(data[1])      # x-position
        y = float(data[2])      # y-position
        return (pid,x,y)

    for i,frame in enumerate(open(fname)):
        #0: Frame, 1: Home, 2: Guest, 3: Referee, 4: Ball
        hash_split = frame.split('#')
        frame_specs = hash_split[0][:-1].split(',')
        # get frame index
        frame = int(frame_specs[0])
        # half time index
        half_time_id[i] = int(frame_specs[2])
        # process home team
        for j, player in enumerate(hash_split[1][:-1].split(';')):
            home_team[i,j,:] = process_player(player)
        # process guest team
        for j,player in enumerate(hash_split[2][:-1].split(';')):
            guest_team[i,j,:] = process_player(player)
        # ball: frame, x, y, z, possession, status
        ball_data = hash_split[4][:-1].split(',')
        x = float(ball_data[0])
        y = float(ball_data[1])
        z = float(ball_data[2])
        poss = float(ball_data[5])
        status = float(ball_data[4])
        ball[i,:] = [frame,x,y,z,poss,status]

    print('finished.')
    return home_team, guest_team, ball, half_time_id

def split_positions_into_game_halves(pos,ht,ball):
    """ splits the data frames into first and second halves.
        Args:
            pos:  position data from read_in_position_data
            ht: half time index form read_in_position_data
        Returns:
            pos_1, pos_2 = position data from game halves.
    """
    res = []
    no_player = pos.shape[1:][0]
    for ht_id in [1,2]:
        ht_idx = ht == ht_id
        no_ht = sum(ht_idx)
        frames = ball[ht_idx,0]
        frames.shape = (no_ht,1,1)
        tmp_pos = np.concatenate((frames.repeat(no_player,1),
                        pos[ht==ht_id,:,:]),2).copy()
        res.append(tmp_pos)

    return res

def sort_position_data(pos,id=1):
    """Sorts the position data according to player and period.

        Args:
            pos: The position data as obtained from read_in_position
        Returns:
            A list with position data from each player.
    """
    unique_player = np.unique(pos[:,:,id])
    res = []
    for pid in unique_player:
        res.append(pos[pos[:,:,id]==pid])
    return res

def read_stadium_dimensions_from_pos(fname):
    """Gets the stadium specifications from the pos file.

        Args:
            fname: name of position file including path.
        Returns:
            Structs with width and length entries.
    """
    fid = open(fname,'r')
    line = fid.readline()
    fid.close()
    specs_string = line.split('#')[5].rstrip()[:-1].split(',')
    length = float(specs_string[1])
    width = float(specs_string[2])
    return dict(length=length ,width=width)

def combine_position_with_role(pos, team):
    """Combines the position data with the players role and pid data.

        Args:
            pos: Position data as obtained thorugh the
                 read_in_position_data_chain.
            team: Team specifications as obtained from MatchInformationParser.
        Returns:
    """
    # build simple dictionary from trikot to role
    trikot_to_role = {}
    trikot_to_pid = {}
    for player in team:
        trikot_to_role[player['trikot']] = player['position']
        trikot_to_pid[player['trikot']] = player['id']
    res = []
    for player in pos:
        trikot = int(player[1,1])
        res.append((trikot_to_pid[trikot],
                    player[:,(0,2,3)],
                    trikot_to_role[trikot]))
    return res

def run(match_info_file, match_pos_file):
    """Driver function to run data loading of impire data.

        Args:
            match_info_file: matchfacts file
            match_pos_file: position data file.
        Returns:
          pos_data: position data struct with keys ['home','guest']
                    with sub struct ['1st','2nd'] for game halves
                    containing list with player entries.
                    [0]: player id
                    [1]: numpy array with frame, x, y data
                    [1]: player role.
                    Position data is not scaled according to pitch dimensions!!!
          ball: numpy array containing the ball data
          match: match information dictionary
          teams: team information dictionary
    """
    from os import path

    # sanity check wheter match info and pos file match up
    fname_1 = path.split(match_info_file)[-1].split('-')[2].split('.')[0]
    fname_2 = path.split(match_pos_file)[-1].split('.')[0]
    if fname_1 != fname_2:
        raise ValueError('fname_specs and fname_pos refer to different games.')

    match, teams = get_impire_match_information(match_info_file, match_pos_file)
    home, guest, ball, half_time_id = read_in_position_data(match_pos_file)

    def process_teams(team,type):
        """Just to work through the team data."""
        periods = split_positions_into_game_halves(team,half_time_id,ball)
        periods_sorted = [sort_position_data(p) for p in periods]
        position_arr = [combine_position_with_role(ps,teams[type])
                            for ps in periods_sorted]
        return position_arr

    home_data = process_teams(home,'home')
    guest_data = process_teams(guest,'guest')
    ball_1 = ball[half_time_id==1,:]
    ball_2 = ball[half_time_id==2,:]

    # Normalize to same dataformat like DFL
    pos_data = dict(
            home = {'1st' : home_data[0], '2nd' : home_data[1]},
            guest = {'1st' : guest_data[0], '2nd' : guest_data[1]})
    ball = [ball_1, ball_2]
    return pos_data, ball, match, teams


def get_impire_match_information(match_info_file, pos_data_file):
    """Simple interface to read in impire matchfacts and team data.

        Args:
            match_info_file: path to the vistrack-matchfacts xml file.
            pos_data_file: path to the position data pos file.
        Returns:
            A tuple with the match info dictionary and the
            teams dictionary.
    """
    mip = MatchInformationParser()
    mip.run(match_info_file)
    teams, match = mip.getTeamInformation()
    match['stadium'] = read_stadium_dimensions_from_pos(pos_data_file)
    return match, teams

def rescale_xy_positions(position_data, ball_data, length, width):
    """Rescales the ball and position data according to the pitch dimensions.

        Args:
            position_data: player position data list
            ball_data: ball position data list
            length: length of pitch 
            width: width of pitch
        Returns:
            The position data list with xy_position scaled accordingly and them
            same for the ball data list

    """
    ball_data_scaled = [ball_data[0].copy(), ball_data[1].copy()]
    position_data_scaled = position_data

    x_scale = length / 2.0
    y_scale = width / 2.0

    for half in ball_data_scaled:
        half[:,1] *= x_scale
        half[:,2] *= y_scale

    for key_t, team_pos_data in position_data_scaled.items():
        for key_h, half in team_pos_data.items():
            for player in half:
                player[1][:,1] = player[1][:,1] * x_scale
                player[1][:,2] = player[1][:,2] * y_scale

    return position_data_scaled, ball_data_scaled


def increase_frame_counter(position_data, ball_data, fh_frame_start = 10000, sh_frame_start = 100000):
    """Changes the frame counter for the first and second half of the ball_data
        Args:
            ball_data: ball data list with first [0] and second half [1]
            fh_frame_start: first half frame counter start
            sh_frame_strat: second half frame counter start 
        Returns:
    """
    ball_data_nf = []
    position_data_nf = position_data

    for half in ball_data:
        ball_data_nf.append(half.copy())
    ball_data_nf[0][:,0] += fh_frame_start 
    ball_data_nf[1][:,0] += sh_frame_start

    for key_t, team_pos_data in position_data_nf.items():
        for key_h, half in team_pos_data.items():
            new_start = fh_frame_start if (key_h == '1st') else sh_frame_start
            for player in half:
                player[1][:,0] = player[1][:,0] + new_start

    return position_data_nf, ball_data_nf

def get_df_from_files(match_info_file, match_pos_file):
    """Wrapper function to get a pandas dataframe from impire position data. 

    This function is meant as an outside API to load position data from
    impire files.

    Args:
        match_info_file: full path to the MatchInformation file.
        match_pos_file: full path to the PositionData file.
    Returns:
        A tuple with a Pandas dataframe with the position data,
        the teams information dictionary, and
        the match information dictionary
    """
    import footballpy.fs.loader.papi as papi

    # read in position data
    pos_data, ball_data, match, teams = run(match_info_file, match_pos_file)
    # rescale to actual meters
    pos_data_sc, ball_data_sc = rescale_xy_positions(pos_data, ball_data, **match['stadium'])
    # add frame counters
    pos_data_reindex, ball_data_reindex = increase_frame_counter(pos_data_sc, ball_data_sc)
    # transform to pandas dataframe
    pos_df = papi.pos_data_to_df(pos_data_reindex, ball_data_reindex)
    return pos_df, teams, match

def get_match_events(match_event_file):
    """Function to parse dfl match events.

        Args:
            match_event_file: full path to match event file.
        Returns:
            a dictionary with event entries.
    """
    from lxml import etree

    def remove_ns_prefix(element_list, ns):
        """Cleans out the namepace of the element list.

            Args:
            Returns:
        """
        new_list = [] 
        for pair in element_list:
            new_list.append((pair[0].replace('{' + ns + '}', ''), pair[1]))
        return new_list
   
    def get_goal_shots(root):
        """Extract the goal shot events. """
        shots = ([remove_ns_prefix(shot.items(), root.nsmap['imp']) 
            for shot in root.xpath('//action-soccer-score-attempt')])
        return shots

    def get_kick_off_whistles(root):
        """Extract the kick-off and final whistles. """
        def extract(root, time, period):
            query_str = '//action-soccer-other[@action-type="period-{0}" and @period-value="{1}"]/@imp:timestamp'
            return root.xpath(query_str.format(time, period), namespaces = root.nsmap)[0]
        whistle_on_first = extract(root, 'start', '1')
        whistle_off_first = extract(root, 'end', '1') 
        whistle_on_second = extract(root, 'start', '2') 
        whistle_off_second = extract(root, 'end', '2')
        return { 'whistle_on_first': whistle_on_first, 'whistle_off_first': whistle_off_first,
                'whistle_on_second': whistle_on_second, 'whistle_off_second': whistle_off_second }

    root = etree.parse(match_event_file).getroot()
    result = dict()

    result['timezone'] = dup.parse(root.xpath('//sports-event/event-metadata/@start-date-time')[0]).tzinfo
    result['goal_shots'] = get_goal_shots(root)
    result['whistle_on_off'] = get_kick_off_whistles(root)

    return result
    

#######################################
if __name__ == "__main__":
    """
    from os import path

    match_info_name = 'vistrack-matchfacts-' + game_name + '.xml'
    fname_match = path.join(path_to_file, match_info_name)
    fname_pos = path.join(path_to_file, game_name + '.pos')

    print("Parsing match information")
    match, teams = get_impire_match_information(fname_match, fname_pos)
    mip = MatchInformationParser()
    mip.run(fname_match)
    teams, match = mip.getTeamInformation()
    match['stadium'] = read_stadium_dimensions_from_pos(fname_pos)
    
    home,guest,ball,half_time_id = read_in_position_data(data_path + fname_pos)
    home_1, home_2 = split_positions_into_game_halves(home,half_time_id,ball)
    home_1s = sort_position_data(home_1)
    home_2s = sort_position_data(home_2)
    
    pos_data_home_1 = combine_position_with_role(home_1s,teams['home'])
    pos_data, ball_data, match, teams = run(path_to_file, match_info_name, match_pos_name)
    pos_data_sc, ball_data_sc = rescale_xy_positions(pos_data, ball_data, **match['stadium'])
    pos_data_reindex, ball_data_reindex = increase_frame_counter(pos_data_sc, ball_data_sc)
    pos_df = get_df_from_files(match_info_file, match_pos_file)
    mep = MatchEventParser()
    mep.run(match_event_file)
    #events = mep.getEvents()
    imp_events = get_match_events(match_events_file)
