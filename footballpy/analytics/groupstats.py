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
