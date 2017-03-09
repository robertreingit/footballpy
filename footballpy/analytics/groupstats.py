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
            pos_data: numpy martix (no_frames X 22) of x-y position data
        Returns:
            Matrix (x X s) containing the length [:,0] and
            width [:,1].
    """
    no_frames = pos_data.shape[0]
    res = np.zeros((no_frames,2))
    res[:,0] = np.max(pos_data[:, 0::2], 1) - np.min(pos_data[:, 0::2], 1)
    res[:,1] = np.max(pos_data[:, 1::2], 1) - np.min(pos_data[:, 1::2], 1)
    return res

def get_team_surface(pos_data):
    """Calculates the team surface using the convex hull.

        Again follows the routines descibed in Frencken et al. (2011).
        Uses the scipy.spatial.ConvexHull function to calculate the
        area.

        Args:
            pos_data: numpy matrix (no_frames x 22) of x-y position data.
        Returns:
            Vector containing the area for each frame.
    """
    from scipy.spatial import ConvexHull
    no_frames = pos_data.shape[0]
    res = np.zeros(no_frames, dtype='float64')
    for i in np.arange(no_frames):
        res[i] = ConvexHull(pos_data[i,:].reshape((11,2))).area
    return res

def get_stretch_index(pos_data):
    """Calculates the team's stretch index following:
        Silva, Travassos, Vilar, Aguiar, Davids, Araújo & Gargata (2014),
        Numerical Relations and Skill Level Constraint Co-Adaptie Behaviors
        of Agents in Sport Teams, PlosONE, 9(9):e107112

        Args:
            pos_data: numpy matrix (no_frames x X) of x-y position data.
        Returns:
    """
    no_frames, no_player = pos_data.shape
    no_player = no_player // 2
    centroid = get_team_centroid(pos_data)
    centroid_exp = np.repeat(centroid, no_player, axis=1)
    tmp = np.zeros((no_frames, no_player))
    for p in np.arange(no_player):
        tmp[:,p] = np.sqrt(np.sum((pos_data[:, (p*2):((p+1)*2)] - centroid)**2, axis=1))
    si = np.mean(tmp, axis=1)
    si.shape = (no_frames, 1)
    return si

def get_team_ranges(pos_data):
    """Calculates the player's ranges following:
        Silva, Travassos, Vilar, Aguiar, Davids, Araújo & Gargata (2014),
        Numerical Relations and Skill Level Constraint Co-Adaptie Behaviors
        of Agents in Sport Teams, PlosONE, 9(9):e107112

        Args:
            pos_data: numpy matrix (no_players x 4) of mid_x, mid_y, std_x, std_y
        Returns:
    """
    no_frames, no_players = pos_data.shape
    no_players = no_players // 2
    mid = np.mean(pos_data, axis=0)
    std = np.std(pos_data, axis=0)
    return np.hstack((mid.reshape((no_players, 2)), std.reshape((no_players, 2))))
