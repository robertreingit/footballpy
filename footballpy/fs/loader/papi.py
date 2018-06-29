# -*- coding: utf-8 -*-
# pylint: disable=C0324
"""
papi: Module which provides a pandas functions to convert
      player and ball position data into a pandas data frame.

@author: rein
@license: MIT
@version 0.1
"""
import numpy as np
import pandas as pd


def collect_pos_data_into_dataframe(pos_data, half_tresh = 100000):
    """Writes the position data from the players into a pandas dataframe for later processing.

        Args:
            pos_data: position data structure
        Returns:
            A dataframe with frameindex and x- and y-positions per player prefixed by ids.
            First half frames usually start with 10000, second half frames start from 100000 but
            can be changed using the half_tresh for the second half.
    """
    def util_1(dataset):
        """Processes team by half position data. """
        dummy_ = []
        for player in dataset:
            dummy_.append(
                    pd.DataFrame(
                    player[1][:,1:],
                    index = (player[1][:,0]).astype(np.int),
                    columns = [player[0]+ '_x',
                        player[0] + '_y']))
        return pd.concat(dummy_, axis=1)

    def util_2(pos_data, team):
        """Concatenate 1st and 2nd halves."""
        data_1st = util_1(pos_data[team]['1st'])
        data_2nd = util_1(pos_data[team]['2nd'])
        return pd.concat([data_1st, data_2nd], sort=False)
    
    home_df = util_2(pos_data, 'home')
    guest_df = util_2(pos_data, 'guest')
    assert(home_df.shape[0] == guest_df.shape[0])
    # add index for half_time
    guest_df['half'] = (guest_df.index >= half_tresh) + 1
    return pd.concat([home_df, guest_df], axis=1)

def collect_ball_data_into_dataframe(ball_data):
    """ Generates a pandas dataframe from the ball position data.

    Args:
    Returns:
    """
    def util_(ball):
        ball_df = pd.DataFrame(
                ball[:,[1,2,4,5]],
                columns = ['ball_x','ball_y','possession','game_state'],
                index = ball[:,0].astype(np.int))
        ball_df['possession'] = ball_df['possession'].astype(np.int)
        ball_df['game_state'] = ball_df['game_state'].astype(np.int)
        return ball_df
    ball_1st = util_(ball_data[0])
    ball_2nd = util_(ball_data[1])
    return pd.concat([ball_1st, ball_2nd])

def pos_data_to_df(pos_data, ball_data):
    """Wrapper function to convert the player and ball position into pandas dataframe.

    Args:
        pos_data: A player position data list
        ball_data: A ball position data list
        
    Returns:
        a pandas data frame containing the position data.
    """
    player_df = collect_pos_data_into_dataframe(pos_data)
    ball_df = collect_ball_data_into_dataframe(ball_data)
    assert(player_df.shape[0] == ball_df.shape[0])
    return pd.concat([player_df, ball_df], axis=1)

