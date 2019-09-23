#!/usr/bin/python3
import numpy as np
from pathlib import Path,os
from misc    import getstatusoutput,os_system,run,copy_all_files,read_files_list
import argparse

"""
Simple python script to test yambo
Author:  C. Attaccalite

Part of the code is copied from scitools of Hans Petter Langtangen 
https://github.com/hplgit/scitools

"""

#############################################
##### DEFAUL TINPUT PARAMETERS ##############
#############################################
yambo_dir     = '/home/attacc/SOFTWARE/devel-nl/bin'
test_dir      = '/home/attacc/SOFTWARE/yambo-tests/TESTS/MAIN/hBN/NL/small'
scratch       = './tmp'  #used to run the tests
yambo_file    = "yambo_nl"
ypp_file      = "ypp_nl"
tollerance    = 0.1 # between 0 and 100%
zero_dfl      = 1e-11
#############################################

# ########################################
# ############## parse command line ######
# ########################################
parser = argparse.ArgumentParser(prog='pytest_yambo',description='Simple python driver for the yambo-tests',epilog="Copyright Claudio Attaccalite 2019")
parser.add_argument('-t',    help='tollerance (between 0 - 100%%)' ,type=float,dest='tollerance',default=tollerance)
parser.add_argument('-s',    help='scratch directory' ,type=str,dest='scratch'    ,default=scratch)
parser.add_argument('-test', help='test directory' ,type=str,dest='test_folder',default=test_dir)
parser.add_argument('-bin',  help='yambo bin directory' ,type=str,dest='yambo_dir',default=yambo_dir)
parser.add_argument('-yambo',help='yambo executable' ,type=str,dest='yambo_file',default=yambo_file)
parser.add_argument('-ypp ', help='ypp exectuable' ,type=str,dest='ypp_file',default=ypp_file)
parser.add_argument('-skip-run',help='skip runs just compare the results',dest='skiprun',action='store_true')
parser.add_argument('-skip-comp',help='skip comparison just run the tests',dest='skipcomp',action='store_true')
parser.set_defaults(skiprun =False)
parser.set_defaults(skipcomp=False)

args = parser.parse_args()
tollerance     = float(args.tollerance)
scratch_dir    = Path(args.scratch)  #used to run the tests
test_folder    = Path(args.test_folder)
yambo_bin      = Path(args.yambo_dir)
yambo          = yambo_bin.joinpath(args.yambo_file)
ypp            = yambo_bin.joinpath(args.ypp_file)

inputs_dir   = test_folder.joinpath("INPUTS")
save_dir     = test_folder.joinpath("SAVE")
reference_dir= test_folder.joinpath("REFERENCE")

##########################################

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
       exit(1)


def convert_wf():
    print("Convert old WF ===>>> new WF....",end='')
    program  =ypp.absolute().as_posix()
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
        exit(1)
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
if not args.skiprun:
    try:
        copy_SAVE_and_INPUTS()
    except:
        print("Error copying SAVE and INPUTS folders to SCRATCH! ")
        exit(1)

# go in the SCRATCH directory
try:
    os.chdir(scratch_dir.as_posix())
except:
    print("Run tests to create all the folders!")
    exit(1)

# convert the WF
if not args.skiprun: convert_wf()


if not args.skiprun:
    #
    # Run all tests
    print("\n\n ********** RUNNING TESTS ***********\n\n")
    #
    for test in tests_list:
        # ************ Running test **************
        print("Running test: "+test.name+"...", end='')

        inputfile=Path("INPUTS/"+test.name).as_posix()

        if "ypp" in test.name:
            # ********* Running ypp **************
            program  =ypp.absolute().as_posix()
        else:
            # ********** Running Yambo ***********
            program  =yambo.absolute().as_posix()

        # ******** Setup flags for the test ******
        flag_file = Path("INPUTS/"+test.name+".flags")
    
        if flag_file.is_file():
            flag_file=open(str(flag_file),"r")
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
            exit(1)
        else:
            print("OK")

if not args.skipcomp:
    print("\n\n ********** COMPARE wiht references ***********\n")
    reference_list=read_files_list(reference_dir,begin='o-')

    for ref in reference_list:
        print("CHECK FILE: "+ref.name+"...", end='')

        if '.ndb' in ref.name:
            print("Database test not implemented yet!")
            continue

        # Open reference file
        ref_file=reference_dir.joinpath(ref.name).as_posix()
        ref_data=np.genfromtxt(ref_file)

        # Open test file
        try:
            test_data=np.genfromtxt(ref.name)
        except:
            print("... not found!!")
            continue

        # Compare data
        for col in range(ref_data.shape[1]):
           diff = np.where(abs(ref_data[:,col])>zero_dfl,abs(ref_data[:,col]-test_data[:,col])/ref_data[:,col],0)
           if np.any(diff>tollerance):
                print("\n    Error in column %d difference larger than %f! " % (col,tollerance),end='') 

        del ref_data,test_data
        print("Done")

