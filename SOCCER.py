# -*- coding: utf-8 -*-
"""
Created on Sat Jun 20 00:09:12 2015

@author: rein
@license: MIT
@version: 0.1
"""
import numpy as np

def write_data_to_file(data, matchname = ''):
    """
    Args:

    Returns:
    """
    if matchname:
        matchname = matchname + '-'
    for ptype in ['home','guest','ball']:
        for ht in [0,1]:
            tmp_data = data[ptype][ht][::25,:]
            num_frames,num_players = tmp_data.shape
            outname = matchname + 'positionen-%s-HT%d' % (ptype,ht)
            with open(outname, 'wb') as f:
                f.write(b'%d\r\n%d\r\n' % (num_frames,num_players))
                np.savetxt(f,tmp_data,fmt='%5.2f',delimiter='  ',newline='  \r\n')

if __name__ == '__main__':
    write_data_to_file(data_transformed)
