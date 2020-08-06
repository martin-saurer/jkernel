#!/usr/bin/env /usr/bin/python3
###############################################################################
# File:        jinter.py
# Author:      Martin Saurer, original 30.12.2017, rewrite 23.02.2020
# Description: Call J from Python.
# License:     GPL Version 3 (see gpl3.txt)
###############################################################################
# -*- coding: utf-8 -*-

###############################################################################
# Import modules
###############################################################################

# Standard Library Imports
import os
import sys
import ctypes
import warnings

###############################################################################
# Utility functions
###############################################################################

# Get exception info
def get_exception_info():
    typ,val,trb = sys.exc_info()
    fil = os.path.split(trb.tb_frame.f_code.co_filename)[1]
    lin = trb.tb_lineno
    est = ('Exception: ' + str(typ) + ': ' + str(val) + ' / in ' + str(fil) +
           ':' + str(lin))
    return est
# end def

# Encode string to utf-8 bytes
def string_encode(s):
    if isinstance(s,str):
        return s.encode('utf-8')
    else:
        return s
    # end if
# end def

# Decode utf-8 bytes to string
def string_decode(s):
    if isinstance(s,str):
        return s
    else:
        return s.decode('utf-8','replace')
    # end if
# end def

# Conmvert byte-encoded integer to int
def bytes_to_int(bytes,byteorder='little'):
    r = int.from_bytes(bytes,byteorder)
    return r
# end def

# Encode int to byte-encoded integer
def int_to_bytes(value,
                 length=ctypes.sizeof(ctypes.c_longlong),
                 byteorder='little'):
    b = int(value).to_bytes(length,byteorder)
    return b
# end def

###############################################################################
# Internal setup
###############################################################################

# We ignore warnings (for now ;-)
#warnings.filterwarnings('ignore')

###############################################################################
# J interpreter class
###############################################################################

# J interpreter class
class J():

    # Constants
    MTYOFM   = 1   # Formatted result array output
    MTYOER   = 2   # Error output
    MTYOLOG  = 3   # Output log
    MTYOSYS  = 4   # System assertion failure
    MTYOEXIT = 5   # Exit
    MTYOFILE = 6   # Output 1!:2[2

    SMWIN    = 0   # Windows front end
    SMJAVA   = 2   # Java front end
    SMCON    = 3   # Console (or shared library)

    # Constructor
    def __init__(self,JInsFol,JBinFol):

        # Members for input/output
        self.JInpRdy = False
        self.JOutRdy = False
        self.JIolRun = True
        self.JWForIn = True
        self.JCurDir = ''
        self.JProStr = ''
        self.JInpStr = ''
        self.JOutStr = ''

        # J Binaries Folder (absolute or relative (to JInsFol) path)
        self.JInsFol = JInsFol
        self.JBinFol = JBinFol

        # J user folder
        self.JUsrFol = ''

        # J Profile (absolute or relative (to JBinFol) path)
        self.JProFil = 'profile.ijs'

        # Declare J variable types for calling JGetM/JSetM
        self.JvrType = ctypes.c_longlong(0)
        self.JvrRank = ctypes.c_longlong(0)
        self.JvrShap = ctypes.c_longlong(0)
        self.JvrData = ctypes.c_longlong(0)

        # Build J Dynamic Library name
        if   sys.platform.startswith('win'   ): self.JDynLib = 'j.dll'
        elif sys.platform.startswith('darwin'): self.JDynLib = 'libj.dylib'
        elif sys.platform.startswith('linux' ): self.JDynLib = 'libj.so'
        else:                                   self.JDynLib = ''

        # Build J path names
        if os.path.isabs(self.JBinFol):
            self.JBin = os.path.join(self.JBinFol)
            self.JLib = os.path.join(self.JBinFol,
                                     self.JDynLib)
            if os.path.isabs(self.JProFil):
                self.JPro = self.JProFil
            else:
                self.JPro = os.path.join(self.JBinFol,
                                         self.JProFil)
            # end if
        else:
            self.JBin = os.path.join(self.JInsFol,
                                     self.JBinFol)
            self.JLib = os.path.join(self.JInsFol,
                                     self.JBinFol,
                                     self.JDynLib)
            if os.path.isabs(self.JProFil):
                self.JPro = self.JProFil
            else:
                self.JPro = os.path.join(self.JInsFol,
                                         self.JBinFol,
                                         self.JProFil)
            # end if
        # end if

        # Declare J callback types
        if sys.platform.startswith('win'):

            self.JInputType  = ctypes.WINFUNCTYPE(ctypes.c_char_p,
                                                  ctypes.c_longlong,
                                                  ctypes.c_char_p)

            self.JWdType     = ctypes.WINFUNCTYPE(ctypes.c_longlong,
                                                  ctypes.c_longlong,
                                                  ctypes.c_longlong,
                                                  ctypes.c_void_p,
                                                  ctypes.c_void_p)

            self.JOutputType = ctypes.WINFUNCTYPE(None,
                                                  ctypes.c_longlong,
                                                  ctypes.c_longlong,
                                                  ctypes.c_char_p)

        else:

            self.JInputType  = ctypes.CFUNCTYPE  (ctypes.c_char_p,
                                                  ctypes.c_longlong,
                                                  ctypes.c_char_p)

            self.JWdType     = ctypes.CFUNCTYPE  (ctypes.c_longlong,
                                                  ctypes.c_longlong,
                                                  ctypes.c_longlong,
                                                  ctypes.c_void_p,
                                                  ctypes.c_void_p)

            self.JOutputType = ctypes.CFUNCTYPE  (None,
                                                  ctypes.c_longlong,
                                                  ctypes.c_longlong,
                                                  ctypes.c_char_p)

        # end if

        # Declare J callback functions
        self.JInputFunc    = self.JInputType(self.JInput)
        self.JWdFunc       = self.JWdType(self.JWd)
        self.JOutputFunc   = self.JOutputType(self.JOutput)
        self.JCallBacks    = [
                                 self.JOutputFunc,
                                 self.JWdFunc,
                                 self.JInputFunc,
                                 0,
                                 ctypes.c_void_p(J.SMCON)
                             ]
        self.JCBArTypes    = (ctypes.c_void_p * len(self.JCallBacks))
        self.JCBArArray    = self.JCBArTypes()
        self.JCBArArray[0] = ctypes.cast(self.JCallBacks[0],ctypes.c_void_p)
        self.JCBArArray[1] = ctypes.cast(self.JCallBacks[1],ctypes.c_void_p)
        self.JCBArArray[2] = ctypes.cast(self.JCallBacks[2],ctypes.c_void_p)
        self.JCBArArray[3] = ctypes.c_void_p(self.JCallBacks[3])
        self.JCBArArray[4] = self.JCallBacks[4]

        # Load J dynamic link library / shareable object
        if sys.platform.startswith('win'):
            self.JDll = ctypes.windll.LoadLibrary(self.JLib)
        else:
            self.JDll = ctypes.cdll.LoadLibrary(self.JLib)
        # end if

        # Declare result type of JInit (this is mandatory !!!)
        self.JDll.JInit.restype = ctypes.c_void_p

        # Initialize J engine
        self.JSession = ctypes.c_void_p(self.JDll.JInit())

        # Register callback functions
        self.JDll.JSM(self.JSession,self.JCBArArray)

        # Setup J environment
        s = self.JDll.JDo(self.JSession,
                          string_encode('ARGV_z_ =: \'\''))
        s = self.JDll.JDo(self.JSession,
                          string_encode('BINPATH_z_ =: \'' + self.JBin + '\''))
        s = self.JDll.JDo(self.JSession,
                          string_encode('0!:0 <\'' + self.JPro + '\''))
        s = self.JDll.JDo(self.JSession,
                          string_encode('NB. 9!:37 (0,16384,0,16000)'))
        s = self.JDll.JDo(self.JSession,
                          string_encode('9!:7 (0{Boxes_j_)'))

    # end def __init__(self,JInsFol,JBinFol)

    ###########################################################################
    # I/O callback functions
    ###########################################################################

    # J input callback
    def JInput(self,j,p):
        return string_encode(input(p.decode('utf-8')))
    # end def

    # J output callback
    def JOutput(self,j,t,s):
        if t == J.MTYOEXIT:
            sys.exit(0)
        # end if
        self.JOutStr += string_decode(s)
        self.JOutRdy = True
    # end def

    # J window driver callback
    # In fact, we use Jwd as an entry point for custom callbacks, using
    # J foreign function 11!:x
    # We read x (int) and the string in struct pa
    # We do not write anything to struct pz
    # Return is always 0
    # mode = x: ...
    # parm = <str>: String Parameter to 11!:x '<str>'
    def JWd(self,j,x,pa,pz):

        # Get mode
        mode = x

        # Get string parameter
        sptr = ctypes.pointer(
                   ctypes.c_longlong(pa +
                       (ctypes.sizeof(ctypes.c_longlong) *
                        ctypes.sizeof(ctypes.c_longlong))))
        parm = ctypes.string_at(sptr.contents.value)
        parm = string_decode(parm)

        # Relevant information is in "mode" and "parm",
        # but we don't use any of these for now
        if mode != 0:
            print('JWd: mode=' + str(mode) + ', parm=\"' + parm + '\"')
        # end if

        # Return 0 (always)
        return 0

    # end def

    ###########################################################################
    # Utility functions
    ###########################################################################

    # Do a J sentence
    def Exec(self,cmd):
        s = self.JDll.JDo(self.JSession,ctypes.c_char_p(string_encode(cmd)))
        return s
    # end def

    # Receive output
    def Recv(self):
        out = ''
        if self.JOutRdy:
            out = self.JOutStr
            self.JOutStr = ''
            self.JOutRdy = False
        # end if
        return out
    # end def

    # Get J string variable
    def GetStrVar(self,var):
        # Declare J variable types for calling JGetM/JSetM
        self.JvrType = ctypes.c_longlong(0)
        self.JvrRank = ctypes.c_longlong(0)
        self.JvrShap = ctypes.c_longlong(0)
        self.JvrData = ctypes.c_longlong(0)
        # Get variable
        sts = self.JDll.JGetM(self.JSession,
                              string_encode(var),
                              ctypes.byref(self.JvrType),
                              ctypes.byref(self.JvrRank),
                              ctypes.byref(self.JvrShap),
                              ctypes.byref(self.JvrData))
        if sts == 0:
            sln = bytes_to_int(ctypes.string_at(self.JvrShap.value,
                               ctypes.sizeof(ctypes.c_longlong)))
            val = ctypes.string_at(self.JvrData.value,sln)
            val = string_decode(val)
            return val
        else:
            return ''
        # end if
    # end def

    # Set J string variable
    def SetStrVar(self,var,val):
        typ = ctypes.c_longlong(2)
        ran = ctypes.c_longlong(1)
        sln = ctypes.c_longlong(len(val))
        sha = ctypes.c_char_p(
                  ctypes.string_at(
                      ctypes.addressof(sln),ctypes.sizeof(ctypes.c_longlong)))
        dat = ctypes.c_char_p(string_encode(val))
        sts = self.JDll.JSetM(self.JSession,
                              string_encode(var),
                              ctypes.byref(typ),
                              ctypes.byref(ran),
                              ctypes.byref(sha),
                              ctypes.byref(dat))
        return sts
    # end def

###############################################################################
# Main Entry Point
###############################################################################

# For testing, here is an example of a Python driven Jconsole
if __name__  == '__main__':

    # Create async J instance
    j = J('/home/martin/J901','bin')
    #j = J('C:\\Users\\martsa-adm\\J901','bin')

    # Run our I/O loop
    while True:

        # Get input
        cmd = input('   ')

        # Exec J sentence
        j.Exec(cmd)

        # Print output
        sys.stdout.write(j.Recv())

    # end while

# end if

###############################################################################
# EOF
###############################################################################

