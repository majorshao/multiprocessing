#!/usr/bin/env python 
# -*- coding: utf-8 -*-


import multiprocessing as mp
import sys
import argparse
import logging
import subprocess
import time
import re
import itertools as it
import fcntl
import errno
import string
import random
import os

class FileFlock:
   """Provides the simplest possible interface to flock-based file locking. 
   Intended for use with the `with` syntax. """

   def __init__(self, path, aString = "abcdef-123", timeout = None):
      self._path = path
      self._timeout = timeout
      self._fd = None
      self._aString = aString.strip()

   def __enter__(self):
      self._fd = os.open(self._path, os.O_APPEND | os.O_WRONLY | os.O_CREAT)
      start_lock_search = time.time()
      while True:

         time.sleep(0.1)
         #print("waiting for lock.....")
         
         try:
            fcntl.flock(self._fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            # Lock acquired!

            for i in range(0,3):
                time.sleep(0.1)
                #print("holding the lock")

            os.write(self._fd, self._aString + "\n")
            return
         except (OSError, IOError) as ex:
            if ex.errno != errno.EAGAIN: # Resource temporarily unavailable
               print("Resource temporarily unavailable")
               sys.exit(1)
            elif self._timeout is not None and time.time() > (start_lock_search + self._timeout):
               # Exceeded the user-specified timeout.
               print("Exceeded the user-specified timeout.")
               sys.exit(1)


   def __exit__(self, *args):
      fcntl.flock(self._fd, fcntl.LOCK_UN)
      os.close(self._fd)
      self._fd = None


def update(tmpfile, HOSTID):
	
    with FileFlock(tmpfile, HOSTID, 3):
        print(HOSTID)
        

def runcmd(L):
    
    print(L)
    
    torun = subprocess.Popen([L], stdout=subprocess.PIPE, shell=True)
    out = torun.stdout.read()
    response = out.decode('utf-8')
    
    print(response)
    
    return response
    

def checker(input, tmpfile):
    """worker function"""
    print("Worker: %s" % input)
    #time.sleep(input*10)

    HOSTID = ""
    if input < 10 :
    	HOSTID = "abc" + str(input) + ".def"
    else:
    	HOSTID = "abc" + str(input) + ".def"


    print(HOSTID)

    torun = "......."

    vmstatus = runcmd(torun)
    result = ""
    print(vmstatus)

    if re.search("No response", vmstatus) or re.search("Nothing matched the target", vmstatus) or re.search("Not connected", vmstatus) :
    	update(tmpfile, HOSTID)
    else:
      result = HOSTID

    sys.stdout.flush()

    return result


result_list = []
def log_result(result):
    # This is called whenever checker(i) returns a result.
    # result_list is modified only by the main process, not the pool workers.
    result_list.append(result)


def apply_async_with_callback():

    
    letters = string.ascii_lowercase
    tmpfile = "/tmp/" + ''.join(random.choice(letters) for i in range(20)) 
    
    runcmd("touch " + tmpfile)
    
    pool = mp.Pool()
    for x in it.chain(range(1, 10), range(10, 301)):
        pool.apply_async(checker, args = (x, tmpfile), callback=log_result)
    pool.close()
    pool.join()
    
    print("Hosts uptime command return ok: ")
    result_list.sort()
    print(result_list)


    print("Hosts return no response to uptime command:")

    with open(tmpfile) as file: 

        print(file.read())

    runcmd("rm -f " + tmpfile)



if __name__ == '__main__':

    apply_async_with_callback()
   





