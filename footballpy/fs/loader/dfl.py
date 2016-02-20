# -*- coding: utf-8 -*-
"""
dfl_parser: Module which provides parsing function for Soccer
            position data. Individual parsers are provided for
            general match information data, match event data,
            and match position data.

@author: rein
@license: MIT
@version 0.1
"""

from __future__ import print_function
import xml.sax, xml.sax.handler
import datetime as dt
import dateutil.parser as dup
import numpy as np
#import ragged_array as ra

class MatchInformationParser(xml.sax.handler.ContentHandler):
    """A XML parser for DFL match information files.
    
    Pulls out the pitch dimensions, and player information.
    Args:
    """

    def __init__(self):
        """Initialization of attributes."""
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
            if role == "home":
                self.inHomeTeam = True
                self.match['home'] = teamID
            elif role == "guest":
                self.inHomeTeam = False
                self.match['guest'] = teamID
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

    def endElement(self,name):
        """Gets called for every closing tag."""
        if name == "Team":
            self.inTeam = False
    
    def getTeamInformation(self):
        """Extractor function."""
        return self.teams, self.match
    
    def run(self,fname):
        """Runs the parse on fname."""
        parser = xml.sax.make_parser()
        parser.setContentHandler(self)
        parser.parse(fname)
        print('finished parsing match information')


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


class Substitution:
    """
    A simple wrapper object for substitution events.
    """
    def __init__(self,time,teamID, pin,pout,position):
        self.time = time
        self.teamID = teamID
        self.pin = pin
        self.pout = pout
        self.position = position
    
    def __repr__(self):
        return ('%s: %s= ->%s - %s->, %s' %  
            (self.time, self.teamID, self.pin, self.pout, self.position))


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
        print('finished parsing event data')
    
    def getEventInformation(self):
        return self.playing_time, self.subs


def calculate_frame_estimate(playing_time,padding_time = 5*60, freq = 25):
    secs_1st = (playing_time['firstHalf'][1] - playing_time['firstHalf'][0]).seconds
    secs_2nd = (playing_time['secondHalf'][1] - playing_time['secondHalf'][0]).seconds
    no_frames = (secs_1st + secs_2nd + padding_time) * freq
    return int(no_frames)

        
class MatchPositionParser(xml.sax.handler.ContentHandler):
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
            if self.teamID == "Ball":
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
        parser = xml.sax.make_parser()
        parser.setContentHandler(self)
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
        
#######################################
if __name__ == "__main__":
    
    data_path = "./test/dfl/"
    fname = 'test.xml'
    
    print("Parsing match information")
    mip = MatchInformationParser()
    fname_match = data_path + "MatchInformation/" + fname
    mip.run(fname_match)
    teams, match = mip.getTeamInformation()
    
    print("Parsing event data")
    mep = MatchEventParser()
    fname_info = data_path + "EventData/" + fname
    mep.run(fname_info)
    play_time, subs = mep.getEventInformation()
    
    print("Parsing position data")
    mpp = MatchPositionParser(match,teams)
    fname_pos = data_path + "/ObservedPositionalData/" + fname
    mpp.run(fname_pos)
    pos_data,ball_data,timestamps = mpp.getPositionInformation()
    
