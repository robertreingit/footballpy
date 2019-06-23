# -*- encoding: utf-8 -*-

import numpy as np
import pandas as pd

def get_state_changes(*state_array, prepend_zero = True, append_max = True):
    """Generates a vector of state change indices from a state vector.

        When multiple state vetors are passed the returned index numpy.array 
        will contain the set of all state changes combined.
        
        Args:
            state_array(s): A numpy array containing indices indicating
                different states.
            prepend_zero: Preppend a zero to the state list.
            append_max: Append the maximum frame number to the state list. If the
                maximum number of frames is appended the state vectors should all have
                the same length.
        Returns:
            A list containing the indices of state changes. 
    """
    state_change_idx = np.where(np.abs(np.diff(state_array[0])) > 0)[0] + 1
    if (len(state_array) > 1):
        for state_i in state_array[1:]:
            state_change_idx = np.concatenate([
                    state_change_idx,
                    np.where(np.abs(np.diff(state_i)) > 0)[0] + 1])
    if prepend_zero:
        state_change_idx = np.concatenate([[0], state_change_idx])
    if append_max:
        max_frame = np.array([state.shape[0] - 1 for state in state_array])
        assert np.all(max_frame == max_frame[0]), 'state arrays must have same length'
        state_change_idx = np.concatenate([state_change_idx, max_frame])
    return np.sort(np.unique(state_change_idx))

if __name__ == '__main__':
    state_1 = np.array([1,1,1,2,2,2,1,1,1,2,2,2])
    print(get_state_changes(state_1))
    state_2 = np.array([1,1,1,2,2,2,3,3,3,2,2,2])
    print(get_state_changes(state_2))
    print(get_state_changes(state_1, state_2))
    state_3 = np.array([0,-1,-1,-1,0,0,0,0,0,-1,-1,-1])
    print(get_state_changes(state_1, state_3))
    state_4 = np.array([0,-1,-1,-1,0,0,0,0,0,-1,-1,-1,-1,-1])
    try:
        print(get_state_changes(state_1, state_4))
    except AssertionError:
        print('correct detection of varying vector lengths.')
    print(get_state_changes(state_1, state_3, prepend_zero = False))
    print(get_state_changes(state_1, state_3, prepend_zero = False, append_max = False))
    print(get_state_changes(state_1, state_3, append_max = False))

