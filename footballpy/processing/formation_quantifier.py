# -*- coding: utf-8 -*-
"""
Created on 26.10.2016.

@author: rein
@license: MIT
@version: 1.0

Some small utility functions to generate time sliced average formations
from impire position data.
"""
#import makepath
import footballpy.fs.loader.impire as imp
import numpy as np
import matplotlib.pyplot as plt

def reshape_pos_data(pos_data, ball, game):
    """
        Simplifies the arrangements of the data from a 3D vector
        into a simple matrix:
        Args:
            pos_data: position data numpy array
            ball: ball data numpy array
            game: game half indicator
        Returns:
            Returns a new matrix with the data.
            The first 5 columns contain game meta-data
            [:,0] = frame indicator
            [:,1] = possession indicator {0,1,2}
            [:,2] = game status {0,1}
            [:,3] = game half {1,2}
            [:,4:] = positions data alternating x-y-position data
            The remaining columns contain the x-y-position data in
            columns 5:26.
    """
    (no_frames, no_players, no_entries) = pos_data.shape
    second_dim = no_players * no_entries
    game_status = ball[:, 4:6]
    game_half = game.copy()
    game_half.shape = (no_frames, 1)
    frames = np.arange(no_frames)
    frames.shape = (no_frames, 1)

    new_pos = pos_data.copy()
    new_pos.shape = (no_frames, second_dim)
    new_pos = np.delete(new_pos, slice(0, second_dim, 3), axis=1) # throw away trikot numbers
    new_pos = np.hstack((frames, game_status, game_half, new_pos))
    return new_pos

def rescale_global_matrix(pos_data, stadium):
    """
        Rescales the x and y positions from [-1,1] to the according stadium dimensions.

        Args:
            pos_data: global position matrix as generated from reshape_pos_data
        Returns:
            The same numpy matrix with the x-y-position scaled.
    """
    new_pos_data = pos_data.copy()
    new_pos_data[:,4:26:2] *= stadium['length']/2.0
    new_pos_data[:,5:26:2] *= stadium['width']/2.0
    return new_pos_data


def determine_cutting_frames(pos_data):
    """Determines the frames were the times-series is split into segments.

        Takes into account the game running status, the possession status, and
        the half-time status. Thus, when ever the games is stopped or the
        possession changes a frame indicator is set.

        Args:
            pos_data: global position matrix as generate from reshape_pos_data
            reshape_pos_data.
        Returns:
            A numpy vector containing cutting indices including 0 for
            the start and the maximum number of frames as the first and
            the last entries.
    """
    def get_pts(dat):
        """ short-cut function to determine when state in dat changes
            Args:
                A numpy vector
            Returns:
                Boolean vector
        """
        return np.where(np.abs(np.diff(dat)) > 0)[0]+1

    # cutting points according to game status
    max_frame = pos_data.shape[0]-1
    poss_cts = get_pts(pos_data[:, 1])
    status_cts = get_pts(pos_data[:, 2])
    half_cts = get_pts(pos_data[:, 3])
    cut_pts = np.unique(np.concatenate([[0], status_cts, half_cts, poss_cts, [max_frame]]))
    return cut_pts

def segment_position_data(pos_data, cut_pts):
    """
        Args:
            pos_data: global position matrix.
            cut_pts: list containing the cutting points required to
                     segment the data.
        Returns:
            A list with individual position data segments for analysis.
    """
    segments = [None]*(len(cut_pts)-1)
    for (i, j) in enumerate(cut_pts[:-1]):
        segments[i] = pos_data[np.arange(cut_pts[i], cut_pts[i+1]), :]
    # Data is filtered for possession indicated by 2nd columm {0, 1, 2}
    # and game status indicated by the 3rd columm {0, 1}
    segments = [segment for segment in segments if np.mean(segment[:, 1]) >= 1.0 and
                np.mean(segment[:, 2]) >= 1.0]
    return segments[1:-1]

def segment_into_time_slices(segments, win_size=125):
    """
        Args:
            segments: A list with game phases.
            win_size: Number of frames for time slice, default=125
        Returns:
            List with continuously stream of time slices. The last
            matrix entries specifies form which possession phase
            this segment came from.
    """
    # iterate through each individual segment
    time_slices = []
    possession_status = []
    for (i, segment) in enumerate(segments):
        # determine the number of time slices
        no_frames = segment.shape[0]
        no_slices = no_frames//win_size + 1
        # interate over each slice
        for sl in range(no_slices):
            start = sl*win_size
            stop = min((sl+1)*win_size, no_frames)
            if start < stop:
                win = slice(sl*win_size, min((sl+1)*win_size, no_frames))
                possession = segment[sl,1]
                possession_status.append(possession)
                av_formation = np.mean(segment[win, 4:], axis=0)
                time_slices.append(np.concatenate([segment[0, :4], av_formation, [i+1]]))
    return time_slices, possession_status

if __name__ == '__main__':
    home_reshaped = reshape_pos_data(home, ball, ht)
    home_s = rescale_global_matrix(home_reshaped, stadium)
    cutting_frames = determine_cutting_frames(home_s)
    home_segments = segment_position_data(home_s, cutting_frames)
    home_slices, possession_slices = segment_into_time_slices(home_segments)

