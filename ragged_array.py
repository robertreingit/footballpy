# -*- coding: utf-8 -*-
"""
ragged_array: some functionality for indexed ragged arrays.

A indexed ragged array as an array which consist of arrays of differnt
lengths buth which contain an index such that the positon of each 
individual array can be located such that they can be mapped into
unique positions of a global array containing missing values.

@author: rein
@license: MIT
@version 0.1
"""
import numpy as np
import pdb

def expand_indexed_ragged_array(ra, row_id, missing_id = -1.234567):
    """Expands an ragged array into one large normal array.

    The function assumes that each array contains a time index
    in the first column and spans only consecutive times points.

    Args:
        ra: ragged array: a list with numpy array entries
        row_id: index into rows
        missing_id = magical number to identify
    Return:
    """
    #pdb.set_trace()
    no_arrays = len(ra)
    no_row_ids = len(row_id)
    max_no_rows = np.max([a.shape[0] for a in ra])
    max_no_cols = np.max([a.shape[1] for a in ra])
    if no_row_ids != max_no_rows:
        raise LookupError("row_id doesn't fit ragged array")

    step = max_no_cols - 1
    result = np.ones((max_no_rows,no_arrays*step)) * missing_id
    for i,ar in enumerate(ra):
        slice_col = slice(i*step,i*step+step)
        slice_row = (row_id >= ar[0,0]) & (row_id <= ar[-1,0])
        result[slice_row,slice_col] = ar[:,1:]

    return result

   
if __name__ == '__main__':
    a1 = np.ones((4,2)); a1[:,0] = np.arange(4)
    a2 = 2*np.ones((6,2)); a2[:,0] = np.arange(6)
    a3 = 3*np.ones((2,2)); a3[:,0] = np.arange(4,6)
    index = np.arange(6)
    test_data = [a1,a2,a3]
    expanded_array = expand_ragged_array(test_data,index)
