#!/usr/bin/python3

from torf import Torrent
import os.path
import sys

base_path = "/media/torrent/unsorted/"

def torrent_cb_verify (ti, f_path_fs, f_path_t, chk_num_files, tot_num_files, exception):
    print (str(chk_num_files) + "/" + str(tot_num_files) + " - " + str(f_path_t))
    if os.path.isfile(str(base_path)+str(f_path_t)):
        print ("OK")
    else:
        print ("DEL")
        os.remove(sys.argv[1])
        os.remove(sys.argv[1]+'.rtorrent')
        os.remove(sys.argv[1]+'.libtorrent_resume')
        sys.exit(10)
    

if os.path.isfile(sys.argv[1]):
    torrent = Torrent.read (sys.argv[1]);
    print ("Torrent Name: "+torrent.metainfo['info']['name'])

    torrent.verify_filesize(base_path,torrent_cb_verify)
