#!/usr/bin/python3
import sys
from subprocess import check_output, CalledProcessError, STDOUT
from pathlib    import os

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


