#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# gPodder PC Import - Import existing Podcast episodes into gPodder
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
import sys
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
debug = False
#
# Podcast file extensions
match_types = ['.m4a','.m4v','.mp3','.mp4','.ogg','.ogv']

def _log(s):
    if debug:
        print(s)
    return

def main():
    # Open Database
    if os.path.exists(db):
        conn = sqlite3.connect(db) or die ("Couldn't open %s" % db)
        # Read Podcast URLS from database
        try:
            pc_result = conn.execute("SELECT id, url FROM episode WHERE url IS NOT NULL")
        except sqlite3.OperationalError:
            print("Invalid db file: %s" % db)
            sys.exit()

        # Build a modified listing from the sql data
        pc_url = []
        for row in pc_result:
            filename, ext = os.path.splitext(row[1].split('/')[-1])
            # Remove URL args when a podcast returns
            if '?' in ext:
                ext = ext.split('?')[0]
            pc_url.append([row[0], '%s%s' % (filename.replace('.', '_'), ext)])

        # Build list of available files in dl_loc
        pc_loc = []
        for root, dirs, files in os.walk(dl_loc, 'topdown=FALSE'):

            # match the podcast
            podcast_name = os.path.split(root)[-1]

            # this is a hack replacing assuming an underscore followed by a
            # space is supposed to be a colon
            podcast_name = podcast_name.replace('_ ',': ')
            try:
                podcast_id = conn.execute("SELECT id from podcast WHERE title = '%s'" % podcast_name).fetchone()[0]
            except:
                podcast_id = None

            # we wont waste out time iter the dir if its not a podcast
            if podcast_id is not None:
                for fname in files:
                    filename, ext = os.path.splitext(fname)
                    if ext in match_types:
                        #pc_loc.append(['%s%s' % (fname[:fname.rfind('_')], ext), fname])
                        pc_loc.append([podcast_id, podcast_name, filename, fname])
                    else:
                        pass # Do Nothing

        # Match file types, update database information
        cntr = 0
        for podcast_id, podcast_name, filename, fname in pc_loc:
            for id, x in pc_url:
                if filename in x:
                    cntr += 1
                    print("FOUND: %s for %s" %
                            (filename, podcast_name))
                    # see if there is already an entry for this so we don't
                    # overwrite they users playback position
                    try:
                        existing = conn.execute("SELECT is_new FROM episode WHERE download_filename = '%s' AND podcast_id = '%d'" % (fname, podcast_id)).fetchone()[0]
                        print("EXIST: Existing entry for %s - %s" %
                                (podcast_name, fname))
                    except:
                        existing = False
                        print("UPDATE: No existing entry found for %s - %s, moving to update" % (podcast_name, fname))

                    # if its new push an update to the db
                    if not existing:
                        try:
                            conn.execute("UPDATE episode SET state = %d, is_new = %d, download_filename = '%s' WHERE id = '%d' AND podcast_id = '%d'" % (state, is_new, fname, id, podcast_id))
                            if sql:
                                conn.commit()
                        except sqlite3.OperationalError as e:
                            print("Failed error was: %s, updating gpodder database" % e)
                else:
                    pass # Do Nothing

        # Print results to screen
        print("EPISODES FOUND: %d" % len(pc_loc))
        print("EPISODES MATCHED TO A PODCAST: %d" % cntr)

        # Close Database
        conn.close()
    else:
        print("Could not find database file: %s" % db)
if __name__ == "__main__":
    main()
