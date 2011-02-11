#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Returns a list of running processes on either Windows or Unix

Detects the OS-type to use the appropriate method. Note that the results
are OS-dependent e.g. giving you more information in a Unix environment.

"""

import os
from ctypes import *


def get_proclist():
    """Return a list of running processes depending on the OS."""
    if os.name == "nt":
        return get_proclist_win()
    else:
        return get_proclist_posix()


def get_proclist_posix():
    """Return a list of running processes on Unix using the /proc folder.

    Note that this method fails on Windows

    """
    pids= [pid for pid in os.listdir('/proc') if pid.isdigit()]
    
    procs = []
    for pid in pids:
        procs.append(open(os.path.join('/proc', pid, 'cmdline'), 'rb').read())

    return procs


def get_proclist_win():
    """
    Enumerates active processes as seen under windows Task Manager on Win NT/2k/XP using PSAPI.dll
    (new api for processes) and using ctypes.Use it as you please.

    Based on information from http://support.microsoft.com/default.aspx?scid=KB;EN-US;Q175030&ID=KB;EN-US;Q175030

    By Eric Koome
    email ekoome@yahoo.com
    license GPL
    """
    psapi = windll.psapi
    kernel = windll.kernel32

    arr = c_ulong * 256
    lpidProcess= arr()
    cb = sizeof(lpidProcess)
    cbNeeded = c_ulong()
    hModule = c_ulong()
    count = c_ulong()
    modname = c_buffer(30)
    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_VM_READ = 0x0010
    
    #Call Enumprocesses to get hold of process id's
    psapi.EnumProcesses(byref(lpidProcess),
                        cb,
                        byref(cbNeeded))
    
    #Number of processes returned
    nReturned = cbNeeded.value/sizeof(c_ulong())
    
    pidProcess = [i for i in lpidProcess][:nReturned]

    procs = []
    
    for pid in pidProcess:
        
        #Get handle to the process based on PID
        hProcess = kernel.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
                                      False, pid)
        if hProcess:
            psapi.EnumProcessModules(hProcess, byref(hModule), sizeof(hModule), byref(count))
            psapi.GetModuleBaseNameA(hProcess, hModule.value, modname, sizeof(modname))
            procs.append("".join([ i for i in modname if i != '\x00']))
            
            #-- Clean up
            for i in range(modname._length_):
                modname[i]='\x00'
            
            kernel.CloseHandle(hProcess)
    
    return procs
