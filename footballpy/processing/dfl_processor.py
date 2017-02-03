# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 23:54:17 2015

@author: rein
@license: MIT
@version: 0.1
"""

from __future__ import print_function
import numpy as np
import footballpy.processing.ragged_array as ra

""" Ranking dictionary necessary to determine the column number
    of each player.
    
    The type system depends on the type of the raw data.
    Type A: Elaborate positioning scheme
    Type B: Simple scheme
    Type C: Amisco-scheme
"""
__position_ranking = {
    'A': {
    'TW':1, 'LV':2, 'IVL':3, 'IVZ':4, 'IVR':5, 'RV':6,
    'DML':7, 'DMZ':8, 'DMR':9,
    'LM':10, 'HL':11, 'MZ': 12, 'HR':13, 'RM':14,
    'OLM':15, 'ZO':16, 'ORM':17,
    'HST':18, 'LA':19, 'STL':20, 'STR':21, 'RA':22,
    'STZ':23
    },
    'B': {
        'G': 1, 'D': 2, 'M': 3, 'A': 4 
    },
    'C': {
        'goalie': 1, 'defenseman': 2, 'mid-fielder': 3, 
        'forward': 4
    }
}


def sort_position_data(pos,type='A'):
    """Sorts the position data according to player positions.

    As the final matrix should contain the player according to their
    position starting from left to right from back to front the indexed
    ragged array list should be sorted such that the entries match
    this format.
    
    Args:
        pos: The list with tuples containing the position data and the
            playing position.
    type: The type of position rankings used by the tracking system. 
        Type A is default.
    Returns:    
        The sorted list.
    """
    ranking_type = __position_ranking[type]
    return sorted(pos,key=lambda player: ranking_type[player[2]])


def stitch_position_data(pos,ball,NO_PLAYERS=11):
    """Puts position data into a single array.
    
    stitch_position_data does not change the ordering of the data and
    stitches the position data together as given. Therefore, if the playing
    position must be controlled sort_position_data must be called first.
    Args:
        pos: position data list (indexed ragged array)
        ball: list with two matrices (1st and 2nd half)
        NO_PLAYERS: default = 11
    Returns:
        output_fields: 
    """
    # magic numbers
    _MISSING_ = -2.0**13
    _NO_DIM_ = 2 # x- and y-coordinates
    _POST_LOOK_ = 20
    # end magic numbers
    
    frames = ball[:,0]
    min_frame = min(frames)
    max_frame = max(frames)
    no_frames = ball.shape[0]
    if no_frames != (max_frame - min_frame + 1):
        raise IndexError("No of ball frames doesn't match")
        
    no_players_input = len(pos)

    input_fields = ra.expand_indexed_ragged_array(pos, frames, 
            lambda x: x[1], _MISSING_)
    input_fields_clean = ra.drop_expanded_ragged_entries(input_fields,NO_PLAYERS*_NO_DIM_,_MISSING_)
    output_fields = ra.condense_expanded_ragged_array(input_fields, missing_id = _MISSING_)
    
    return output_fields


def determine_playing_direction(goalie):
    """ Determines the teams' playing direction.
    
    Determines the playing direction using
    the average position of the goalie.

    Args:
        goalie: x-y position of goalie
    Returns:
        either 'l2r': left to right or 'r2l': right to left.
    """
    return 'l2r' if np.average(goalie[:,0]) < 0 else 'r2l'


def switch_playing_direction(position_coords):
    """Switches the position coordinates.
    
    Mirrors the position coordinates either from left to right or vice versa.
    The routine assumes that the origin (0,0) is localized at the width and 
    length midpoints.
        -----------------
        |             |
        |_            |
        | |         (0,0)
        |_|           |
        |             |
        |             |
        -----------------
    Args:
        position_coords: x-y position coordinates of the players.
    Returns:
        Nothing, the matrix coordinates are flipped in place.
    """
    # just mirrors the x-coordinate in place
    position_coords[:,0::2] *= -1


def rescale_playing_coords(position_coords,pitch_dim):
    """Relocates the origin to left-bottom and rescales to [0,10] height/width.
    
    The routine assumes that the origin (0,0) is localized at the width and 
    length midpoints.
        -----------------
        |             |
        |_            |
        | |         (0,0)
        |_|           |
        |             |
        |             |
        -----------------
    Args:
        position_coords:
        pitch_dim:
    Returns:
        Nothing, the matrix coordinates are scaled in place.
    """
    pitch_width = pitch_dim['width']
    pitch_length = pitch_dim['length']
    # translate to bottom-left corner
    position_coords[:,0::2] += pitch_length/2           # x-coordinates
    position_coords[:,1::2] += pitch_width/2            # y-coordinates
    # rescale to [0,10]
    position_coords[:,0::2] *= 10.0/pitch_length        # x-coordinates
    position_coords[:,1::2] *= 10.0/pitch_width         # y-coordinates


def clamp_values(result,vmin=0.0, vmax=10.0):
    """Clamps the position values to [0,10]

    Args:
        result:
        vmin: minimum value
        vmax = maximum value
    Returns:
        None. Matrix is clamped in place.
    """
    for entry in result:
        for ht in result[entry]:
            ht[ht<vmin] = vmin
            ht[ht>vmax] = vmax


def run(pos_data,ball_data,match,ranking_type='A'):
    """Driver routine to run all processing steps.
    
        Args:
            ranking_type: Specifies which postion_ranking system should be used.
        Returns:
    """
    roles = ['home','guest']
    sections = ['1st','2nd']
    result = {'home':[0]*2, 'guest':[0]*2, 'ball':[0]*2}
    
    # switch for l2r switching mode
    l2r_section = 0

    # processing player position data first    
    for sec in sections:
        home_direction = 'r2l'
        for role in roles:
            print('Processing: %s-%s...' % (role,sec))
            sorted_pos_data = sort_position_data(pos_data[role][sec], ranking_type)
            stitched_data = stitch_position_data(sorted_pos_data,ball_data[sec!='1st'])
            if role == 'home':
                home_direction = determine_playing_direction(stitched_data[:,0:2])
            if home_direction == 'l2r':
                switch_playing_direction(stitched_data)
                l2r_section = 0 if sec=='1st' else 1
            rescale_playing_coords(stitched_data,match['stadium'])
            result[role][0 if sec=='1st' else 1] = stitched_data
            print('done')
    
    # processing ball data
    print('Processing ball...')
    switch_playing_direction(ball_data[l2r_section][:,1:3])
    for i in [0,1]:
        rescale_playing_coords(ball_data[i][:,1:3],match['stadium'])
    result['ball'][0] = ball_data[0][:,1:3]
    result['ball'][1] = ball_data[1][:,1:3]

    #correct value ranges.
    print('clamping values.')
    clamp_values(result)
    print('done.')
    return result
            
    
if __name__ == '__main__':
#teams, match, pos_data,ball_data
    section = '2nd'
    kk = pos_data['home'][section]    
    kks = sort_position_data(kk)
    bb = ball_data[section!='1st']
    ss = stitch_position_data(kks,bb)
    data_transformed = run(pos_data,ball_data,match)
