# -*- coding: utf-8 -*-
"""
ragged_array: some functionality for indexed ragged arrays.

A indexed ragged array is a list which consist of objects containing
somewhere numpy arrays with different row lengths.
Each of these numpy arrays contains an index in the first column
such that the positon of each individual array can be located.
Resulting in a unique positions in a global array containing missing values.
Kind of similar to a sparse array.

@author: rein
@license: MIT
@version 0.1
"""
import numpy as np
import pdb

def expand_indexed_ragged_array(ra, row_id, accessor = lambda x: x, missing_id = -1.234567):
    """Expands an ragged array into one large normal array.

    The function assumes that each individual array contains a time index
    in the first column and spans only consecutive times points. The objects
    contained in the list a more complex an accessor functions must be
    provided which can extract the array. Default is the identity function.

    Args:
        ra: ragged array: a list with numpy array entries
        accessor: function to obtain values from list. 
                  Default is idenitity function.
        row_id: index into rows
        missing_id = magical number to identify
    Returns:
        An numpy array with the entries from the ragged array in the according
        time index positions.
    """

    #pdb.set_trace()
    no_arrays = len(ra)
    no_row_ids = len(row_id)
    max_no_rows = np.max([accessor(a).shape[0] for a in ra])
    max_no_cols = np.max([accessor(a).shape[1] for a in ra])
    if no_row_ids != max_no_rows:
        raise LookupError("row_id doesn't fit ragged array")

    step = max_no_cols - 1
    result = np.ones((max_no_rows,no_arrays*step)) * missing_id
    for i,ar in enumerate(ra):
        tmp_data = accessor(ar)
        slice_col = slice(i*step,i*step+step)
        slice_row = (row_id >= tmp_data[0,0]) & (row_id <= tmp_data[-1,0])
        result[slice_row,slice_col] = tmp_data[:,1:]

    return result
   
if __name__ == '__main__':
    a1 = np.ones((4,2)); a1[:,0] = np.arange(4)
    a2 = 2*np.ones((6,2)); a2[:,0] = np.arange(6)
    a3 = 3*np.ones((2,2)); a3[:,0] = np.arange(4,6)
    index = np.arange(6)
    test_data = [a1,a2,a3]
    expanded_array = expand_indexed_ragged_array(test_data,index)
