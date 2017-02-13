# -*- coding: utf-8 -*-
"""
single_frame_parser: Loads the raw position data and game data using
                     a different format.

@author: rein
@license: MIT
@version: 0.1
"""
import xml.sax, xml.sax.handler
import numpy as np
import os

def get_data_files(folder):
    """Determines the position data files.
    Args:
    Returns:
    """
    raw_pos_files = [f for f in os.listdir(data_folder) if f.startswith('Put')]
    raw_pos_files.sort()
    no_files = len(raw_pos_files)
    max_no_frames = no_files * 25
    return raw_pos_files, max_no_frames


class GameStatsParser(xml.sax.handler.ContentHandler):
    """A XML parser for the game stats xml file.

    The parser pulls out the information about the teams, including
    the players, their id, and where available their position.
    """

    def __init__(self):
        self.inLineup = False
        self.teams = {'home': [], 'guest': [] }
        self.match = {'stadium': {'length': 111.0, 'width': 88.0 },
                        'home': '', 'guest': '' }
    
    def startElement(self,name,attrs):
        if name ==  "Team":
            role = attrs['sType']
            teamID = attrs['iTeamId']
            if role == 'Home':
                self.inHomeTeam = True
                self.match['home'] = teamID
            elif role == 'Away':
                self.inHomeTeam = False
                self.match['guest'] = teamID
            else:
                raise NameError("Couldn't determine role")
        elif name == "Lineup":
            self.inLineup = True
        elif name == "Player" and self.inLineup:
            name = attrs['sFirstName'] + ':' + \
                    attrs['sLastName']
            pid = attrs.getValue('iId')
            trikot = int(attrs['iJerseyNo'])
            position = attrs['sPos']
            player = {"id": pid, "name": name, "trikot": trikot,
                    "position": position }
            if self.inHomeTeam:
                self.teams['home'].append(player)
            else:
                self.teams['guest'].append(player)

    def endElement(self,name):
        if name == "Lineup":
            self.inLineup = False

    def getTeamInformation(self):
        return self.teams, self.match

    def run(self,name):
        parser = xml.sax.make_parser()
        parser.setContentHandler(self)
        parser.parse(fname)


class PositionFileParser(xml.sax.handler.ContentHandler):
    """A XML Parser for a PutPositionalDataRequest file.

    Parses out the position data.
    """

    def __init__(self):
        self.inPosition = False
        self.counter = 0
        self.line = ''

    def startElement(self,name,attrs):
        if name == "Positions":
            self.inPosition = True
    
    def characters(self,data):
        if self.inPosition:
            if not data or (data == "\n") or (data == ']'):
                return
            if data.startswith('CDATA'):
                data = data[6:]
            if data.startswith('-1'):
                return
            process_line(data)

    def endElement(self,name):
        if name == "Positions":
            self.inPosition = False

    def run(self,fname):
        parser = xml.sax.make_parser()
        parser.setContentHandler(self)
        parser.parse(fname)

class FloodArray:
    """Stores consecutive vectors into a matrix.

    Just a thin wrapper to a numpy array useful when
    it is not clear how many points are needed but all points
    should be stored consecutively.
    Attributes:
        max_rows: maximum number of possible rows in matrix.
        no_cols: number of cols.
        array: underlying numpy array
        current_row: running counter storing current position
    """

    def __init__(self, max_rows=10000, no_cols=4, expand_step=1000):
        """ Constructor method.

        Args:
            max_rows: number of rows { default: 10000 }
            no_cols: number of columns { default: 4}
            expand_step: number of rows the matrix is expanded when maximum
                      row size is reached. { default: 1000 }
        Returns:
            Nothing
        """
        self.max_rows = max_rows
        self.expand = expand_step 
        self.no_cols = no_cols
        self.array = -13 * np.ones((max_rows, no_cols))
        self.current_row = 0

    def push(self, data):
        """Pushes a new vector onto the matrix.

        Args:
            data: a new vector.
        Returns:
            Nothing
        """
        if self.current_row + 2 == self.max_rows:
            no_rows, no_cols = self.array.shape
            self.array.resize((no_rows + self.expand, no_cols), refcheck=False)
        self.array[self.current_row,:] = data
        self.current_row += 1

    def data(self):
        """Returns the current data.
        Args:
            Nothing
        Returns:
            A numpy matrix containing the data.
        """
        return self.array[:self.current_row,:].copy()


def process_line(line):
    """ Processes a single line from a put file.
    Args:
    Returns:
    """
    frame_specs,players,ball = line.split('#')
    # processing player
    frame = float(frame_specs.split(',')[0])
    players = filter(lambda x: x.startswith('p'), players.split(';'))
    for player in players:
        pid,xs,ys,vels = player.split(',')
        x = float(xs)
        y = float(ys)
        pid = pid[1:]
        if pid in guest_col_id.keys():
            guest_res[guest_col_id[pid]].push(np.array([frame,x,y,0.0]))
        else:
            home_res[home_col_id[pid]].push(np.array([frame,x,y,0.0]))
    # processing ball
    xs,ys,zs = ball.split(',')[:3]
    x = float(xs)
    y = float(ys)
    z = float(zs)
    ball_res.push(np.array([frame,x,y,z]))


