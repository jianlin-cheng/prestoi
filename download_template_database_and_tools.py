#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import re
import glob
import subprocess, argparse

def makedir_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    directory = os.path.abspath(directory)
    return directory

def rm_if_exists(directory):
    if os.path.exists(directory):
        directory = os.path.abspath(directory)
        if os.path.isdir(directory):
            os.system("rm -r "+directory)
        else:
            os.system("rm "+directory)

def direct_download(tool, address, tools_dir, unzip=True):  ####Tools don't need to be configured after downloading and configuring
    os.chdir(tools_dir)
    tool_dir = os.path.join(tools_dir, tool)
    if not os.path.exists(tool_dir):
        rm_if_exists(tool_dir)
        os.system("wget "+address)
        print("Decompressing "+tool_dir)
        if unzip:
            os.system("tar -zxf "+tool+".tar.gz && rm "+tool+".tar.gz")
            os.system("chmod -R 755 "+tool_dir)
        else:
            os.system("chmod -R 755 "+tool_dir)
        print("Downloading "+tool_dir+"....Done")
    else:
        print(tool+" has been installed "+tool_dir+"....Skip....")


if __name__ == '__main__':
    # Set directory of multicom databases and tools
    install_dir = os.path.dirname(os.path.realpath(__file__))
    database_dir = os.path.join(install_dir, 'databases')
    tools_dir = os.path.join(install_dir, "tools")
    makedir_if_not_exists(database_dir)
    makedir_if_not_exists(tools_dir)

    ### (1) Download basic tools
    os.chdir(tools_dir)
    tools_lst = ["hhsuite-3.2.0"]
    for tool in tools_lst:
        address = "http://sysbio.rnet.missouri.edu/multicom_cluster/multicom3_db_tools/tools/"+tool+".tar.gz"
        direct_download(tool, address, tools_dir)
     
    ### (2) Download databases
    os.chdir(database_dir)

    db_lst = ["pdb_sort90_2024"]
    for db in db_lst:
        print("Download "+db)
        if os.path.exists(os.path.join(database_dir, db)):
            continue
        direct_download(db,"http://sysbio.rnet.missouri.edu/multicom_cluster/multicom3_db_tools/databases/"+db+".tar.gz",database_dir)

    db_lst = ["uniref90_Pre-CASP16.fasta"]
    for db in db_lst:
        print("Download "+db)
        if os.path.exists(os.path.join(database_dir, db)):
            continue
        direct_download(db,"http://sysbio.rnet.missouri.edu/multicom_cluster/multicom3_db_tools/databases/"+db,database_dir, unzip=False)

    print("\nConfiguration....Done")
