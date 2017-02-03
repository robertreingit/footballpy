# -*- encoding: utf-8 -*-
"""
game_events: Collection of functions working on game events.

@author: rein
@license: MIT
@version: 0.1
"""

from __future__ import print_function
from scipy import signal
import numpy as np

def find_shot_frame(player_xy, ball_xy, threshold=1.7, freq=25.0, filter_freq=2.0):
    """Finds the frame instance of the shot using a simple distance approach.
    Args:
        player_xy: numpy array with xy-coordinates
        ball_xy: numpy array with xy-coordinates
        threshold: minimum distance between player and ball {default: 1.7m}.
        freq: recording frequency of position data.
        filter_freq: filter frequency used for smoothing distance data.
    Returns: Frame number 0 if event is not found and filter distance for debugging.
    """
    # calculate distance between player and ball
    d = np.sqrt(np.sum( (player_xy - ball_xy)**2, axis=1))

    # generate filter
    b,a = signal.butter(2, filter_freq/(freq/2.0))
    d_filt = signal.filtfilt(b, a, d)

    try:
        # first occurence where distance is smaller than threshold
        start_idx = np.where(d_filt < threshold)[0][-1]
        # go backwards and find minimum distance between player and ball
        while (d_filt[start_idx] > d_filt[start_idx-1]) & (start_idx > 0):
            start_idx -= 1
    except IndexError:
        print("Couldn't determine shooting frame")
        start_idx = 0 

    return start_idx,d_filt

