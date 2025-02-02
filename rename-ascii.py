#!/usr/bin/python3
import os
import string

src_dir = '.'
os.chdir(src_dir)

for file_name in os.listdir(src_dir): 
    new_file_name = ''.join(c for c in file_name if c in string.printable)
    print (" -> " + str(new_file_name))
    os.rename(os.path.join(src_dir,file_name), os.path.join(src_dir, new_file_name))
