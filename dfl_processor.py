# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 23:54:17 2015

@author: rein
@license: MIT
@version: 0.1
"""
import numpy as np

""" Ranking dictionary necessary to determine the column number
    of each player.
    
    The type system depends on the type of the raw data.
    Type A: Elaborate positioning scheme
    Type B: Simple scheme
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
	}
}

def sort_position_data(pos,type='A'):
    """Sorts the position data according to player positions.
    
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

def stitch_position_data(pos,ball):
    """Puts position data into a single array.
    
    stitch_position_data does not change the ordering of the data and
    stitches the position data together as given. Therefore, if the playing
    position must be controlled sort_position_data must be called first.
    Args:
        pos:
        ball:
    Returns:
    """
    # magig numbers
    NO_OUTPUT_PLAYERS = 11
    # end magic numbers
    
    frames = ball[:,0]
    min_frame = min(frames)
    max_frame = max(frames)
    no_frames = ball.shape[0]
    if no_frames != (max_frame - min_frame + 1):
        raise IndexError
        
    no_player = len(pos)
    input_fields = np.ones((no_frames,no_player*2), dtype='float32')*-100
    # populate input fields
    for pidx in range(no_player):
        frames_present = (frames>=pos[pidx][1][0,0]) & (frames<=pos[pidx][1][-1,0])
        # determine frame slice
        slice_idx = slice(pidx*2,pidx*2+2)
        input_fields[frames_present,slice_idx] = pos[pidx][1][:,1:3]
    
    # transferring present data from input field into output_field    
    output_fields = np.ones((no_frames,NO_OUTPUT_PLAYERS*2), dtype='float32')*-1
    for row in range(no_frames):
        # determine valid entries in current row
        player_idx = input_fields[row,:]>-100
        output_fields[row,slice(0,sum(player_idx))] = input_fields[row,player_idx]
    return output_fields
    
def determine_playing_direction(goalie):
    """ Determiners the team playing direction.
    
    determine_playing_direction determines the playing direction using
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
    Returns:
    """
    pitch_width = pitch_dim['width']
    pitch_length = pitch_dim['length']
    # translate to bottom-left corner
    position_coords[:,0::2] += pitch_length/2           # x-coordinates
    position_coords[:,1::2] += pitch_width/2            # y-coordinates
    # rescale to [0,10]
    position_coords[:,0::2] *= 10.0/pitch_length        # x-coordinates
    position_coords[:,1::2] *= 10.0/pitch_width         # y-coordinates
    

def run(pos_data,ball_data,match):
    """Driver routine to run all processing steps.
    
    Args:
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
            print 'Processing: %s-%s...' % (role,sec)
            sorted_pos_data = sort_position_data(pos_data[role][sec])
            stitched_data = stitch_position_data(sorted_pos_data,ball_data[sec!='1st'])
            if role == 'home':
                home_direction = determine_playing_direction(stitched_data[:,0:2])
            if home_direction == 'l2r':
                switch_playing_direction(stitched_data)
                l2r_section = 0 if sec=='1st' else 1
            rescale_playing_coords(stitched_data,match['stadium'])
            result[role][0 if sec=='1st' else 1] = stitched_data
            print 'done'
    
    # processing ball data
    print 'Processing ball...'
    switch_playing_direction(ball_data[l2r_section][:,1:3])
    for i in [0,1]:
        rescale_playing_coords(ball_data[i][:,1:3],match['stadium'])
    result['ball'][0] = ball_data[0][:,1:3]
    result['ball'][1] = ball_data[1][:,1:3]
    print 'done.'
    
    return result
            
    
if __name__ == '__main__':
#teams, match, pos_data,ball_data
    section = '2nd'
    kk = pos_data['home'][section]    
    kks = sort_position_data(kk)
    bb = ball_data[section!='1st']
    ss = stitch_position_data(kks,bb)
    data_transformed = run(pos_data,ball_data,match)
