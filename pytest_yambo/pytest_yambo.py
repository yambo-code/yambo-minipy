#!/usr/bin/python3
import numpy as np
from pathlib import Path,os
from misc    import getstatusoutput,os_system,run,copy_all_files,read_files_list

"""
Simple python script to test yambo
Author:  C. Attaccalite

Part of the code is copied from scitools of Hans Petter Langtangen 
https://github.com/hplgit/scitools

"""

#############################################
############# INPUT PARAMETERS ##############
#############################################
yambo_bin     = Path('/home/attacc/SOFTWARE/devel-nl/bin')
test_folder   = Path('/home/attacc/SOFTWARE/yambo-tests/TESTS/MAIN/hBN/NL/small')
scratch_dir   = Path('./tmp')  #used to run the tests
yambo_file    = "yambo_nl"
ypp_file      = "ypp_nl"
tollerance    = 0.1 # between 0 and 100%
#############################################


inputs_dir   = test_folder.joinpath("INPUTS")
save_dir     = test_folder.joinpath("SAVE")
reference_dir= test_folder.joinpath("REFERENCE")
yambo        = yambo_bin.joinpath(yambo_file)
ypp          = yambo_bin.joinpath(ypp_file)

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
        print("REFERENCE folder is..."+str(reference_dir.is_dir())+"; ")
    except:
       print(" KO!\n")


def convert_wf():
    print("Convert old WF ===>>> new WF....",end='')
    program  =yambo_bin.joinpath(ypp_file).absolute().as_posix()
    options  ="-w c"
    failure=run(program=program,options=options,logfile="conversion_wf.log")
    if failure: 
        print("KO!")   
        exit(0)
    else:
        print("OK")   

    print("Rename FixSAVE,SAVE ===>>> SAVE, oldSAVE....",end='')
    try:
        oldSAVE=Path('SAVE')
        oldSAVE.rename('oldSAVE')
        FixSAVE=Path('FixSAVE/SAVE')
        FixSAVE.rename('SAVE')
    except:
        print("KO!")
    print("OK")


def copy_SAVE_and_INPUTS():
    new_save=scratch_dir.joinpath('SAVE/')
    Path(new_save).mkdir(parents=True,exist_ok=True)
    copy_all_files(save_dir,new_save)

    new_inputs_dir=scratch_dir.joinpath('INPUTS/')
    Path(new_inputs_dir).mkdir(parents=True,exist_ok=True)
    copy_all_files(inputs_dir,new_inputs_dir)


# 
# ************* MAIN PROGRAM ********************
#
print("\n * * * Yambo python tests * * * \n\n")

#check the code
check_code()

#read test list
tests_list=read_files_list(inputs_dir,noext='.flags')
print("\nNumber of tests: "+str(len(tests_list)))

# copy SAVE and INPUTS in the SCRATCH directory 
copy_SAVE_and_INPUTS()

# go in the SCRATCH directory
os.chdir(scratch_dir)

# convert the WF
convert_wf()

# Run all tests
for test in tests_list:
    # ************ Running test **************
    print("Running test: "+test.name+"...", end='')

    inputfile=Path("INPUTS/"+test.name).as_posix()

    if "ypp" in test.name:
        # ********* Running ypp **************
        program  =yambo_bin.joinpath(ypp_file).absolute().as_posix()
    else:
        # ********** Running Yambo ***********
        program  =yambo_bin.joinpath(yambo_file).absolute().as_posix()

    # ******** Setup flags for the test ******
    flag_file = Path("INPUTS/"+test.name+".flags")
    
    if flag_file.is_file():
        flag_file=open(flag_file,"r")
        flag=flag_file.read().strip()
        flag_file.close()
        previous_test_dir=Path(flag)
        new_test_dir     =Path(test.name)
        Path(new_test_dir).mkdir(parents=True,exist_ok=True)
        copy_all_files(previous_test_dir,new_test_dir)


    options=" -J "+test.name

    # ****** run yambo or ypp *****************
    failure=run(program=program,options=options,inputfile=inputfile,logfile=test.name+".log")

    if(failure):
        print("KO!")
        exit(0)
    else:
        print("OK")

#********** COMPARE with references ************************
#for test in test_list:

