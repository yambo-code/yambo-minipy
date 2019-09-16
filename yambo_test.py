#!/usr/bin/python3
import numpy as np
from pathlib import Path,os
import scitools.Regression

"""
Simple python script to test yambo
Author:  C. Attaccalite
"""

########################
# INPUT PARAMETERS     #
########################
yambo_bin    = Path('/home/attacc/SOFTWARE/devel-nl/bin')
test_folder  = Path('/home/attacc/SOFTWARE/yambo-tests/TESTS/MAIN/hBN/NL/small')
yambo_file  = "yambo_nl"
ypp_file    = "ypp_nl"
#########################


inputs_dir   = test_folder.joinpath("INPUTS")
save_dir     = test_folder.joinpath("SAVE")
reference_dir= test_folder.joinpath("REFERENCE")
yambo = yambo_bin.joinpath(yambo_file)
ypp   = yambo_bin.joinpath(ypp_file)

def check_code():
    print("Checking codes and foldes: ")
    try:
        print("Yambo bin is..."+str(yambo_bin.is_dir())+"; ", end = '')
        print("Test folder is..."+str(test_folder.is_dir())+"; ", end = '')
        print("Yambo is..."+str(yambo.exists())+"; ", end = '')
        print("Ypp is..."+str(ypp.exists()))
        print("\nChecking sub-folders: ")
        print("SAVE folder is..."+str(save_dir.is_dir())+"; ", end = '')
        print("INPUTS folder is..."+str(inputs_dir.is_dir())+"; ", end = '')
        print("REFERENCE folder is..."+str(reference_dir.is_dir())+"; ", end = '')
    except:
       print(" KO!\n")

print("\n * * * Yambo python tests * * * \n\n")

check_code()



