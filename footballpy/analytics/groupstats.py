# -*- encoding: utf-8 -*-
"""
A collection of functions to perform groups statistics on position data.

@author: Robert Rein
@version: 0.1
"""
import numpy as np

def get_team_centroid(pos_data):
    """Calcuates the team centroid from position data.

        If the position data contains nans those are excluded.

        Args:
            pos_data: numpy matrix (x X 22) of x-y position data
        Returns:
            Matrix (x X 2) containing the team centroid measures.
    """
    x_centroid = np.nanmean(pos_data[:,::2],1, keepdims = True)
    y_centroid = np.nanmean(pos_data[:,1::2],1, keepdims = True)
    return np.hstack((x_centroid, y_centroid))

def get_team_length_and_width(pos_data):
    """Calculates the team length and width according.

        Uses the approach described in:
        Frencken, Lemmink, Delleman & Visscher (2011)
        Oscillations of centroid position and surface area
        of soccer teams in small-sided games.
        European Journal of Sport Science, 11(4), 215-223. 

        Args:
            pos_data: numpy marix (x X 22) of x-y position data
        Returns:
            Matrix (x X s) containing the length [:,0] and
            width [:,1].
    """
    no_frames = pos_data.shape[0]
    print(no_frames)
    res = np.zeros((no_frames,2))
    res[:,0] = np.max(pos_data[:, 0::2], 1) - np.min(pos_data[:, 0::2], 1)
    res[:,1] = np.max(pos_data[:, 1::2], 1) - np.min(pos_data[:, 1::2], 1)
    return res
