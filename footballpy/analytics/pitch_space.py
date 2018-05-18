# -*- coding: utf-8 -*-
"""
Created on Monday 07.05.2018

@author: rein
@license: MIT
@version: 0.1
"""

from __future__ import print_function
import numpy as np

def create_pitch_grid(pitch, side_length = 0.5):
    """Create a pitch grid datastructure.

    Args:
        pitch: tuple (width, length) containing the pitch dimensions.
        side_length: length of the grid sides {default. 0.5}
    Returns:
        a tuple with:
        a numpy array with two rows (convention):
            1st row: x position of grid point
            2nd row: y position of grid point,
        The area assigned to each grid point.
    """
    no_horizontal_cells = int(pitch[0] / side_length)
    no_vertical_cells = int(pitch[1] / side_length)

    pitch = np.zeros((no_horizontal_cells * no_vertical_cells, 2))
    for row in range(no_vertical_cells):
        for col in range(no_horizontal_cells):
            idx_x = row * no_horizontal_cells  + col
            pitch[idx_x, 0] = side_length / 2.0 + side_length * col
            pitch[idx_x, 1] = side_length / 2.0 + side_length * row

    return pitch, side_length**2


def assign_grid_pts_to_players(pitch_grid, players):
    """Assigns grid points to players according to the smallest euclidean distance.

    Args:
        pitch_grid: numpy array with 2 rows and x columns each providing the mid-point
                of a grid point
        players: numpy array with x frames by y rows and 2 columns each providing the 
                position of a player for frame.
    Returns:
    """
    no_frames = players.shape[0]
    cell_to_player = np.zeros((pitch_grid.shape[0], no_frames), dtype=np.uint16)
    for frame in range(no_frames):
        for i,cell in enumerate(pitch_grid):
            distance_to_grid = np.sqrt(np.sum((cell - players[frame,])**2, 1))
            min_index = np.argmin(distance_to_grid)
            cell_to_player[i, frame] = min_index
    return cell_to_player

def calculate_pitch_space_per_player(winner, no_players, cell_area):
    """Calculate the space assigned to teach player.

    Args:
        winner: assignment of pitch space to player.
        no_players: number of players to generate space map.
        cell_area: area of each individual space.
    Returns:
    """
    no_frames = winner.shape[1]
    space_controlled = np.zeros((no_players, no_frames))
    for frame in range(no_frames):
        for player in range(no_players):
            space_controlled[player, frame] = cell_area * np.sum(winner[:,frame] == player)
    return space_controlled

def clip_pitch_grid(grid, length_cut_off, width_cut_off, high_pass = True):
    """Clips the pitch grid to a smaller grid.

    Args:
        grid: numpy array specifying the grid points.
        length_cut_off, width_cut_off: cut of points in x and y direction.
        high_pass: Determins whether cut off points are used for high
                    pass of low pass. High pass cut-points are inclusive.
    Returns:
        a pitch grid without the according grid points and
        a mask to identify assigned players.
    """
    if high_pass:
        mask  = np.logical_and(grid[:,0] >= width_cut_off,  grid[:,1] >= length_cut_off)
    else:
        mask = np.logical_and(grid[:,0] < width_cut_off,  grid[:,1] < length_cut_off)

    return grid[mask,], mask


if __name__ == '__main__':
    grid, grid_cell_area = create_pitch_grid((10,3), 1)
    print(grid)
    players = np.array(
            [[[.2, .2],[2.0,1.0],[3.2,1.2]],
            [[.1, .1], [.3,.3],[2.1,1.1]]])
    winner = assign_grid_pts_to_players(grid, players)
    print(winner)
    grid_clipped, mask = clip_pitch_grid(grid, 1.0, 1.0)
    space_controlled = calculate_pitch_space_per_player(winner, 3, grid_cell_area)
    print(space_controlled)

