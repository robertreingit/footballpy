# -*- coding: utf-8 -*-

"""
dfl_batch: does the whole trick with a batch of files

@author: raabe
@license: MIT
@version 0.1
"""

import os
import dfl_parser as prs
import dfl_processor as prc
import dfl_writer as wrt


def matchdir(directory):
    """
    Creates a directory for the converted match and adjusts cwd.

	Args: Directory to create/change into.
	Returns: Nothing
    """
    if not os.path.exists(directory):
        os.mkdir(directory)
    os.chdir(directory)
        
###############################################################################

if __name__ == "__main__":

    # --> SPECIFY DATA PATHS HERE PLEASE <-- #
    data_path = "rawdata"
    batch_path = data_path + "/league/"
    out_path = "outdata"
    
    # Pulling out the list of matches from one of the folders.
    batch = os.listdir(batch_path)
    
    for counter,fname in enumerate(batch):
        print "CONVERTING MATCH %d of %d: %s\n\n" % (counter,len(batch),fname)
        fname_match = data_path + "MatchInformation/BL/" + fname
        fname_info = data_path + "Events/BL/" + fname
        fname_pos = data_path + "ObservedPositionalData/BL/" + fname
        matchname = os.path.splitext(fname)[0]
    
        # Runs the parser
        print "Parsing match information"
        mip = prs.MatchInformationParser()
        mip.run(fname_match)
        teams, match = mip.getTeamInformation()
        print "Parsing event data"
        mep = prs.MatchEventParser()
        mep.run(fname_info)
        play_time, subs = mep.getEventInformation()
        print "Parsing position data"
        mpp = prs.MatchPositionParser(match,teams)
        mpp.run(fname_pos)
        pos_data,ball_data = mpp.getPositionInformation()
        
        # Runs the processor
        section = '2nd'
        kk = pos_data['home'][section]
        kks = prc.sort_position_data(kk)
        bb = ball_data[section!='1st']
        ss = prc.stitch_position_data(kks,bb)
        data_transformed = prc.run(pos_data,ball_data,match)
        
        # Runs the writer
        print "Step 3: Saving Information\n"
        matchdir(out_path+matchname)
        wrt.write_data_to_file(data_transformed,matchname)
        
