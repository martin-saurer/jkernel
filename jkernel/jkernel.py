###############################################################################
#
# File:        jkernel.py
# Author:      Martin Saurer, 19.02.2016
# Description: Jupyter / J - integration.
#
# License:     GPL Version 3 (see gpl3.txt)
#
# Note 1:      To enforce python run in 32bit mode on Mac OS X,
#              set the following environment variable:
#              export VERSIONER_PYTHON_PREFER_32_BIT=yes
#
###############################################################################

###############################################################################
# Import modules
###############################################################################

# Imports
import os
import sys
import base64

# Import Jupyter Kernel
from ipykernel.kernelbase import Kernel

# Append this files path to sys.path
sys.path.append(os.path.dirname(__file__))

# Import J interface
import jinter

###############################################################################
# Global variables
###############################################################################

canvasnum = 1

###############################################################################
# Jupyter Kernel Class
###############################################################################

# Jupyter Kernel Class
class JKernel(Kernel):

    # Basic kernel setup
    implementation         = 'jkernel'
    implementation_version = '3.2.0'
    language_info          = {
        'name'            : 'J',
        'mimetype'        : 'text/J',
        'file_extension'  : 'ijs'
    }
    banner                 = 'J Programming Language - Jupyter Kernel'
    help_links             = [
        {
            'text': 'Vocabulary',
            'url':  'http://www.jsoftware.com/help/dictionary/vocabul.htm'
        },
        {
             'text': 'NuVoc',
             'url':  'http://www.jsoftware.com/jwiki/NuVoc'
        }
    ]

    # Constructor
    def __init__(self, *args, **kwargs):
        # Call super class constructor
        super(JKernel,self).__init__(*args,**kwargs)

        # Get required OS environment variables
        JInsFol = os.getenv('J_INSTALLATION_FOLDER')
        JBinFol = os.getenv('J_BIN_FOLDER')

        # Initialize J
        self.J = jinter.J(JInsFol,JBinFol)

        # Initialize J JHS
        self.J.Exec('IFJHS_z_ =: 1')
        self.J.Exec('canvasnum_jhs_ =: 1')
        self.J.Exec('load \'jhs\'')

        # This one is not defined on Windows ???
        if os.name == 'nt':
            self.J.Exec('iad_pplatimg_ =: 15!:14@boxopen')
        # end if

        # Get J user folder
        self.J.Exec('tmpstr_jinter_ =: jpath \'~user\'')
        s = self.J.GetStrVar('tmpstr_jinter_')
        if os.name == 'nt':
            s = s.replace('/','\\')
        else:
            s = s.replace('\\','/')
        # end if
        self.J.JUsrFol = s
    # end def

    # Override do_execute method
    def do_execute(self,
                   code,
                   silent,
                   store_history=True,
                   user_expressions=None,
                   allow_stdin=False):

        # Global variables
        global canvasnum

        # Debug output
        #self.log.error('*** do_execute')

        # Initialization
        output = ''

        # Split cell into single lines
        lines = code.splitlines()

        # Pass input to J (new version)
        # Multi-line statements (like verb definitions) are now possible
        # Only the output of the last line (statement) is printed
        lines = [line for line in lines if line.strip() != '']
        lastline = ''
        if len(lines) > 0:
            # Check last line (end of multiline statement)
            if not lines[-1].strip() == ')':
                lastline = lines[-1]
                del lines[-1]
                code = '\n'.join(lines)
            # end if
        # end if

        # Prepare code
        code = code.replace('\'','\'\'')

        # Execute code
        self.J.Exec('input_jinter_ =: \'' + code + '\'')
        self.J.Exec('0!:110 input_jinter_')

        # Process last line (receive output)
        if lastline.strip() != '':
            self.J.Exec(lastline)
            output = self.J.Recv()
        # end if

        # Check silent flag
        if not silent:

            # Debug output
            #self.log.error('*** not silent')

            # Check output length
            if len(output) > 0:

                # Debug output
                #self.log.error('*** len(output) > 0')
                #self.log.error('*** ' + self.J.JUsrFol)

                # Check output
                if output.startswith('<!-- j html output a -->'):

                    # Error handler
                    try:

                        # Is it an image output ?
                        prefix = '<!-- j html output a --><img'
                        if output.startswith(prefix):

                            # Extract image name
                            stapos = output.find('src=')
                            imgnam = output[stapos+11:]
                            endpos = imgnam.find('?')
                            imgnam = imgnam[:endpos]
                            imgnam = os.path.join(self.J.JUsrFol,
                                                  'temp',
                                                  imgnam)

                            # Read image in base64 encoded data
                            with open(imgnam,'rb') as fp:
                                imgdat = base64.b64encode(fp.read()).decode()
                            # end with
                            try:
                                os.remove(imgnam)
                            except:
                                pass
                            # end try

                            # Send output data
                            content = {
                                'source'   : 'J',
                                'metadata' : { },
                                'data'     : {'image/png': imgdat}
                            }
                            #self.log.error(repr(content))
                            self.send_response(self.iopub_socket,
                                               'display_data',
                                               content)

                        # Other output (plot)
                        else:

                            # Generate HTML file name
                            htmnam = os.path.join(self.J.JUsrFol,
                                                  'temp',
                                                  'plot.html')

                            # Read html file
                            with open(htmnam,'r') as fp:
                                htmdat = fp.read()
                                htmdat = htmdat.replace('</article>',
                                        '</article><script>graph();</script>')
                                htmdat = htmdat.replace('canvas1',
                                        'canvas' + str(canvasnum))
                            # end with
                            try:
                                os.remove(htmnam)
                            except:
                                pass
                            # end try

                            # Increment canvasnum
                            canvasnum += 1

                            content = {
                                'source'   : 'J',
                                'metadata' : { },
                                'data'     : {'text/html': htmdat}
                            }
                            self.send_response(self.iopub_socket,
                                               'display_data',
                                               content)

                        # end if output.startswith(prefix):

                    except:
                        # Error output
                        content = {
                            'name': 'stdout',
                            'text': ('JKernel: Internal Error.\n' +
                                     str(sys.exc_info()[1]) +
                                     '\n')
                        }
                        self.send_response(self.iopub_socket,'stream',content)

                    # end try
                  
                # Is it an html output
                elif output.startswith('<html>'):
                    content = {
                        'source':   'J',
                        'metadata': { },
                        'data':     {'text/html': output}
                    }
                    self.send_response(self.iopub_socket,
                                       'display_data',
                                       content)

                else:
                    # Normal text output
                    content = {
                        'name': 'stdout',
                        'text': output
                    }
                    self.send_response(self.iopub_socket,'stream',content)

                # end if output.startswith('<!-- j html output a -->'):

            # end if len(output) > 0:

        # end if not silent:

        # Return
        return {
            'status':           'ok',
            'execution_count':  self.execution_count,
            'payload':          [],
            'user_expressions': {},
        }

    # end def do_execute()

    # Nothing special here
    def do_shutdown(self,restart):
        pass

    def do_inspect(self,code,cursor_pos,detail_level=0):
        pass

# end class JKernel(Kernel):

# Main entry point
if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=JKernel)
# end if

###############################################################################
# EOF
###############################################################################
