# -*- encoding: utf-8 -*-
"""
cassandra:  Module providing interface to talk to a local Apache Cassandra instance. 
            At the moment experimental, doesn't do much usefull.

@author: rein
@license: MIT
@version 0.1
"""
from cassandra.cluster import Cluster
import numpy as np

__TEST_KEYSPACE__ = 'soccer_test'
__cluster__ = Cluster()
__session__ = __cluster__.connect(__TEST_KEYSPACE__)

def init():
    """ Drops the test table in test keyspace and creates a
        new one.
    """
    query1 = """
        DROP TABLE IF EXISTS position_data;
        """
    query2 = """
        CREATE TABLE position_data (
            game_id text,
            half int,
            team_id text,
            player_id text,
            frame int,
            x_pos float,
            y_pos float,
            PRIMARY KEY ((game_id), half, team_id, player_id, frame)
        );
        """
    __session__.execute(query1)
    __session__.execute(query2)

def insert_player(game_id, half, team_id, player_id, xy):
    """Puts all the data from one player into the table.
    """
    query = """
        INSERT INTO position_data (
            game_id,
            half,
            team_id,
            player_id,
            frame,
            x_pos,
            y_pos)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    for row in xy:
        __session__.execute(query, 
            (game_id, half, team_id, player_id, int(row[0]), row[1], row[2]))

def get_player_position_data(game_id, half, team_id, player_id):
    """ Experimental function to retrieve position data for one player.
        Args:
        Returns:
            An numpy array with the position data.
    """
    query = """
        SELECT frame, x_pos, y_pos FROM position_data
        WHERE game_id = %s
        AND half = %s
        AND team_id = %s
        AND player_id = %s;
    """
    res = __session__.execute(query, (game_id, half, team_id, player_id))
    # as the size of the array is not known in advance
    # storing the individual rows into a list which
    # is subsequently cast into a numpy array.
    arr = []
    for row in res:
        arr.append(row)
    return np.array(arr)

def close():
    """ Closes the cluster connection.
    """
    __cluster__.shutdown()



if __name__ == '__main__':
    init()
    #insert_player('123','456',np.array([[0, 1.0, 2.0],[1, 10.0, 20.0]]))
    #insert_player(str(game_id), player_id, player_xy)
    insert_player( game_id, half, team_id, player_id, player_xy)
    close()
    #p_data = get_player_position_data(game_id, player_id)

