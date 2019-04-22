###############################################################################
#
# File:        jinter.py
# Author:      Martin Saurer, 30.12.2017
# Description: Jupyter jkernel interface.
#
# License:     GPL Version 3 (see gpl3.txt)
#
###############################################################################

###############################################################################
# Import modules
###############################################################################

import os
import sys
import time
import warnings

from ctypes import *

###############################################################################
# Default setup
###############################################################################

# J installation folder
JInsFol = os.getenv('J_INSTALLATION_FOLDER')

# J binaries folder
JBinFol = os.getenv('J_BIN_FOLDER')

###############################################################################
# Utility functions (Mainly for Python 2/3 compatibility)
###############################################################################

# Print exception info
def print_exception_info():
    typ,val,trb = sys.exc_info()
    fil = os.path.split(trb.tb_frame.f_code.co_filename)[1]
    lin = trb.tb_lineno
    est = ('Exception: ' + str(typ) + ': ' + str(val) + ' / in ' + str(fil) +
           ':' + str(lin))
    print('>>>>>>>> ' + est)

# Encode to utf-8 if python version is 2
def string_encode2(s):
    if sys.version_info[0] == 2:
        return s.encode('utf-8')
    else:
        return s

# Encode to utf-8 if python version is not 2 (assumed 3)
def string_encode3(s):
    if sys.version_info[0] == 2:
        return s
    else:
        if isinstance(s,str):
            return s.encode('utf-8')
        else:
            return s

# Decode to bytes if python version is 2
def string_decode2(s):
    if sys.version_info[0] == 2:
        return s.decode('utf-8','replace')
    else:
        return s

# Decode to bytes if python version is not 2 (assumed 3)
def string_decode3(s):
    if sys.version_info[0] == 2:
        return s
    else:
        if isinstance(s,str):
            return s
        else:
            return s.decode('utf-8','replace')

# Decode unicode escapes in python 2
def string_decode_escapes(s):
    if sys.version_info[0] == 2:
        return s.decode('unicode-escape')
    else:
        return s

# Handle input
def string_input(p):
    if sys.version_info[0] == 2:
        return raw_input(p)
    else:
        return input(p)

###############################################################################
# Internal setup
###############################################################################

# We ignore warnings (for now ;-)
warnings.filterwarnings('ignore')

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
    def __init__(self):

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
        self.JBinFol = JBinFol

        # J user folder
        self.JUsrFol = ''

        # J Profile (absolute or relative (to JBinFol) path)
        self.JProFil = 'profile.ijs'

        # Build J Dynamic Library name
        if   sys.platform.startswith('win'   ): self.JDynLib = 'j.dll'
        elif sys.platform.startswith('darwin'): self.JDynLib = 'libj.dylib'
        elif sys.platform.startswith('linux' ): self.JDynLib = 'libj.so'
        else:                                   self.JDynLib = ''

        # Build J path names
        if os.path.isabs(self.JBinFol):
            self.JBin = os.path.join(self.JBinFol)
            self.JLib = os.path.join(self.JBinFol,self.JDynLib)
            if os.path.isabs(self.JProFil):
                self.JPro = self.JProFil
            else:
                self.JPro = os.path.join(self.JBinFol,self.JProFil)
        else:
            self.JBin = os.path.join(JInsFol,self.JBinFol)
            self.JLib = os.path.join(JInsFol,self.JBinFol,self.JDynLib)
            if os.path.isabs(self.JProFil):
                self.JPro = self.JProFil
            else:
                self.JPro = os.path.join(JInsFol,self.JBinFol,self.JProFil)

        # Declare types for calling JGetM
        self.JType = pointer(c_long())
        self.JRank = pointer(c_long())
        self.JShap = pointer(c_long())
        self.JData = pointer(c_char_p())

        # Declare J callback types
        if sys.platform.startswith('win'):
            self.JInputType  = WINFUNCTYPE(c_char_p,c_long,c_char_p)
            self.JWdType     = WINFUNCTYPE(c_long,c_long,c_long,c_void_p,c_void_p)
            self.JOutputType = WINFUNCTYPE(None,c_long,c_long,c_char_p)
        else:
            self.JInputType  = CFUNCTYPE(c_char_p,c_long,c_char_p)
            self.JWdType     = CFUNCTYPE(c_long,c_long,c_long,c_void_p,c_void_p)
            self.JOutputType = CFUNCTYPE(None,c_long,c_long,c_char_p)

        # Declare J callback functions
        self.JInputFunc    = self.JInputType(self.JInput)
        self.JWdFunc       = self.JWdType(self.JWd)
        self.JOutputFunc   = self.JOutputType(self.JOutput)
        self.JCallBacks    = [self.JOutputFunc,
                              self.JWdFunc,
                              self.JInputFunc,
                              0,
                              c_void_p(J.SMCON)]
        self.JCBArTypes    = (c_void_p * len(self.JCallBacks))
        self.JCBArArray    = self.JCBArTypes()
        self.JCBArArray[0] = cast(self.JCallBacks[0],c_void_p)
        self.JCBArArray[1] = cast(self.JCallBacks[1],c_void_p)
        self.JCBArArray[2] = cast(self.JCallBacks[2],c_void_p)
        self.JCBArArray[3] = c_void_p(self.JCallBacks[3])
        self.JCBArArray[4] = self.JCallBacks[4]

        # Load J dynamic link library / shareable object
        if sys.platform.startswith('win'):
            self.JDll = windll.LoadLibrary(self.JLib)
        else:
            self.JDll = cdll.LoadLibrary(self.JLib)

        # Declare result type of JInit (this is mandatory !!!)
        self.JDll.JInit.restype = c_void_p

        # Initialize J engine
        self.JSession = c_void_p(self.JDll.JInit())

        # Register callback functions
        self.JDll.JSM(self.JSession,self.JCBArArray)

        # Setup J environment
        s = self.JDll.JDo(self.JSession,
                          string_encode3('ARGV_z_ =: \'\''))
        s = self.JDll.JDo(self.JSession,
                          string_encode3('BINPATH_z_ =: \'' + self.JBin + '\''))
        s = self.JDll.JDo(self.JSession,
                          string_encode3('0!:0 <\'' + self.JPro + '\''))
        s = self.JDll.JDo(self.JSession,
                          string_encode3('NB. 9!:37 (0,16384,0,16000)'))
        s = self.JDll.JDo(self.JSession,
                          string_encode3('9!:7 (0{Boxes_j_)'))
        s = self.JDll.JDo(self.JSession,
                          string_encode3('IFJHS_z_ =: 1'))
        s = self.JDll.JDo(self.JSession,
                          string_encode3('canvasnum_jhs_ =: 1'))
        s = self.JDll.JDo(self.JSession,
                          string_encode3('load \'jhs\''))

        # This one is not defined on Windows ???
        s = self.JDll.JDo(self.JSession,
                          string_encode3('iad_pplatimg_ =: 15!:14@boxopen'))

        # Get J user folder
        s = self.JDll.JDo(self.JSession,
                          string_encode3('tmpstr_jinter_ =: jpath \'~user\''))
        s = self.JDll.JGetM(self.JSession,
                            string_encode3('tmpstr_jinter_'),
                            self.JType,
                            self.JRank,
                            self.JShap,
                            self.JData)
        s = string_at(self.JData.contents.value)
        s = string_decode3(s)
        if os.name == 'nt':
            s = s.replace('/','\\')
        else:
            s = s.replace('\\','/')
        self.JUsrFol = s

    ###########################################################################
    # I/O callback functions
    ###########################################################################

    # J input callback
    def JInput(self,j,p):
        return string_encode3(input(p.decode('utf-8')))

    # J output callback
    def JOutput(self,j,t,s):
        if t == J.MTYOEXIT:
            sys.exit(0)
        self.JOutStr += string_decode3(s)
        self.JOutRdy = True

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
        sptr = pointer(c_long(pa+8*sizeof(c_long)))
        parm = string_at(sptr.contents.value)
        parm = string_decode3(parm)

        # Relevant information is in "mode" and "parm",
        # but we don't use any of these for now
        #print('JWd: mode=' + str(mode) + ', parm=\"' + parm + '\"')

        # Return 0 (always)
        return 0

    ###########################################################################
    # Utility functions
    ###########################################################################

    # Do a J sentence
    def Exec(self,cmd):
        s = self.JDll.JDo(self.JSession,c_char_p(string_encode3(cmd)))
        return s

    # Receive output
    def Recv(self):
        out = ''
        if self.JOutRdy:
            out = self.JOutStr
            self.JOutStr = ''
            self.JOutRdy = False
        return out

###############################################################################
# Main Entry Point
###############################################################################

# For testing, here is an example of a Python driven Jconsole
if __name__  == '__main__':

    # Create async J instance
    j = J()

    # Run our I/O loop
    while True:

        # Get input
        if sys.version_info.major == 2:
            cmd = raw_input('   ')
        else:
            cmd = input('   ')

        # Exec J sentence
        j.Exec(cmd)

        # Print output
        sys.stdout.write(j.Recv())

###############################################################################
# EOF
###############################################################################

