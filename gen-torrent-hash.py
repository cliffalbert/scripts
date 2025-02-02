#!/usr/bin/python3 
import libtorrent as lt
torrent = open('example.torrent','rb').read()
info = lt.torrent_info(torrent, len(torrent))
info_hash = info.info_hash()
hexadecimal = str(info_hash)
integer = int(hexadecimal, 16)
