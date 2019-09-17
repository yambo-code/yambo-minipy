#!/usr/bin/python3
import numpy as np
import sys
from pathlib import Path,os
from shutil import copyfile
from subprocess import check_output, CalledProcessError, STDOUT

"""
Simple python script to test yambo
Author:  C. Attaccalite

Part of the code is copied from scitools of Hans Petter Langtangen 
https://github.com/hplgit/scitools

"""

########################
# INPUT PARAMETERS     #
########################
yambo_bin     = Path('/home/attacc/SOFTWARE/devel-nl/bin')
test_folder   = Path('/home/attacc/SOFTWARE/yambo-tests/TESTS/MAIN/hBN/NL/small')
scratch_dir   = Path('./tmp')  #used to run the tests
yambo_file    = "yambo_nl"
ypp_file      = "ypp_nl"
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
        print("REFERENCE folder is..."+str(reference_dir.is_dir())+"; ")
    except:
       print(" KO!\n")
	
def getKey(custom):
    return custom.name

def read_test_list():
    flist = []
    for p in inputs_dir.iterdir():
        if p.is_file():
            if not p.name.endswith(".flags"):
                flist.append(p)

    flist=sorted(flist,key=getKey)
    print("\nNumber of tests: "+str(len(flist)))
#    for test in flist: print(test)
    return flist

def getstatusoutput(cmd):
    try:
        data = check_output(cmd, shell=True, universal_newlines=True, stderr=STDOUT)
        status = 0
    except CalledProcessError as ex:
        data = ex.output
        status = ex.returncode
    if data[-1:] == '\n':
        data = data[:-1]
    return status, data


def os_system(command, verbose=True, failure_handling='exit', fake=False):
    """
    User-friendly wrapping of the os.system/os.popen commands.
    Actually, the commands.getstatusoutput function is used on Unix
    systems, and the output from the system command is fetched.

    ================  ========================================================
    ================  ========================================================
    command           operating system command to be executed
    verbose           False: no output, True: print command prior to execution
    failure_handling  one of 'exit', 'warning', 'exception', or 'silent'
                      (in case of failure, the output from the command is
                      always displayed)
    fake              if True, the command is printed but not run (for testing)
    return value      the same as commands.getstatusoutput, i.e., a boolean
                      failure variable and the output from the command as a
                      string object
    ================  ========================================================
    """
    if verbose:
        print('\nRunning operating system command:  %s' % command)
    if fake:
        return 0, 'testing "%s"' % command

    if sys.platform[:3] == 'win':
        result = os.popen(command)
        output = result.read()
        failure = result.close()
    else:
        # Unix/Linux/Mac:
        failure, output = getstatusoutput(command)

    if failure:
        msg = 'Failure when running operating system command'\
              '\n  %s\nOutput:\n%s' % (command, output)
        if failure_handling == 'exit':
            print(msg, '\nExecution aborted!')
            sys.exit(1)
        if failure_handling == 'warning':
            print('Warning:', msg)
        elif failure_handling == 'exception':
            raise OSError(msg)
        elif failure_handling == 'silent':
            pass
        else:
            raise ValueError('wrong value "%s" of failure_handling' % \
                             failure_handling)

    return failure, output



def run(program='',options='', inputfile='',logfile='logfile'):
    """Run program, store output on logfile."""
    # the logfile is always opened in the constructor so
    # we can safely append here

    vfile = open(logfile, 'a')
    vfile.write('\n#### Test: %s' % (program+"_"+inputfile))
    vfile.write(' running %(program)s %(options)s\n' % vars())
    vfile.close()

    # do not use time.clock() to measure CPU time; it will not
    # notice the CPU time(here waiting time) of a system command
    t0 = os.times()  # [user,system,cuser,csystem,elapsed]
    cmd = '%s %s -F %s >> %s' % (program,options,inputfile,logfile)
    failure, output = os_system(cmd, failure_handling='silent')
    if failure:
        vfile = open(logfile, 'a')
        msg = 'ERROR in execution failure arose from the ' \
              'command\n  %s\n\n%s\n\n' % (cmd,output)
        vfile.write(msg)
        vfile.close()
        print(msg)
    # write CPU time of system command(user+system time
    # of child processes):
    t1 = os.times(); tm = t1[2] - t0[2] + t1[3] - t0[3]
    vfile = open(logfile, 'a')
    vfile.write('CPU time of %(program)s: %(tm).1f seconds' % vars())
    if os.name == 'posix':  # is 'posix', 'nt' or 'mac'
        # unix
        u = os.uname()
        vfile.write(' on %s %s, %s' % (u[1],u[4],u[0]))
    vfile.write('\n\n')
    vfile.close()










# 
# ************* MAIN PROGRAM ********************
#
print("\n * * * Yambo python tests * * * \n\n")

check_code()

test_list=read_test_list()

# check if scratch folder exists or create it and copy SAVE 
new_save=scratch_dir.joinpath('SAVE/')
Path(new_save).mkdir(parents=True,exist_ok=True)
for p in save_dir.iterdir():
    copyfile(p,new_save.joinpath(p.name))
os.chdir(scratch_dir)

for test in test_list:
    # ************ Running test **************
    print("Running test: "+test.name+"...", end='')

    inputfile=inputs_dir.joinpath(test.name).absolute().as_posix()

    if "ypp" in test.name:
        # ********* Running ypp **************
        program  =yambo_bin.joinpath(ypp_file).absolute().as_posix()
    else:
        # ********** Running Yambo ***********
        program  =yambo_bin.joinpath(yambo_file).absolute().as_posix()

    # ******** Setup flags for the test ******
    my_file = inputs_dir.joinpath(test.name+".flags")
    
    options=""
    if my_file.is_file():
        flag_file=open(my_file,"r")
        flag=flag_file.read()
        options=options+" -O "+flag
        flag_file.close()

    options=options+" -J "+test.name

#    print("\nProgram:  "+program)
#    print("Options:  "+options)
    test_ok=run(program=program,options=options,inputfile=inputfile,logfile=test.name+".log")

    test_ok=True
    if(test_ok):
    # *********** Compare the results ********
        print(test_ok)
    else:
        print("KO!")
#
