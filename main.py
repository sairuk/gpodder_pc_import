#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# gPodder_pc_Import - Import existing Podcast episodes into gPodder
# Copyright (c) 2014 Wayne Moulden
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
import os
import sqlite3
#
###############################################################################
# Settings (Should be easily modifiable to software other than PA)
# Edit items below if your configuration and/or requirement differ from the 
# default installation, add in filetypes as required.
#
db = 'Database' # gPodder database file (relative to script)
dl_loc = 'Downloads' # gPodder podcast download location (relative to script)
state = 1 # Episode State (1=Downloaded, 2=Deleted)
is_new = 1 # Is the episode new? (0=No, 1=Yes)
sql = True # Set to False to disable SQL commits while testing
#
# Podcast file extensions
match_types = ['.m4a','.m4v','.mp3','.mp4','.ogg','.ogv']

def main():
    # Open Database
    conn = sqlite3.connect(db) or die ("Couldn't open %s" % db)
    # Read Podcast URLS from database
    pc_result = conn.execute("SELECT id, url FROM episode WHERE url IS NOT NULL")

    # Build a modified listing from the sql data
    pc_url = []
    for row in pc_result:
        filename, ext = os.path.splitext(row[1].split('/')[-1])
        # Remove URL args when a podcast returns
        if '?' in ext:
            ext = ext.split('?')[0]
        pc_url.append([row[0],'%s%s' % (filename.replace('.','_'),ext)])

    # Build list of available files in dl_loc
    pc_loc = []
    for root, dirs, files in os.walk(dl_loc, 'topdown=FALSE'):
        for fname in files:
            filename, ext = os.path.splitext(fname)          
            if ext in match_types:
                pc_loc.append(['%s%s' % (fname[:fname.rfind('_')],ext),fname])
            else:
                pass # Do Nothing
                

    # Match file types, update database information
    cntr = 0
    for row2, fname in pc_loc:
        for id, x in pc_url:
            if row2 in x:
                cntr += 1
                try:
                    print "FOUND: %s, updating gpodder database" % (row2)
                    conn.execute("UPDATE episode SET state = %d, is_new = %d, download_filename = '%s' WHERE id = '%d'" % (state,is_new,fname,id))
                    if sql:
                        conn.commit()
                except:
                    pass # Do Nothing
            else:
                pass # Do Nothing
                
    # Print results to screen
    print "OLD EPISODES FOUND: %d" % len(pc_loc)
    print "OLD EPISODES MATCHED: %d" % cntr
    
    # Close Database
    conn.close() 
    
if __name__ == "__main__":
    main()