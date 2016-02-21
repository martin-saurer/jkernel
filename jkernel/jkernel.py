################################################################################
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
################################################################################

################################################################################
# Import modules
################################################################################

# Imports
import os
import sys
import time
import base64

# Import Jupyter Kernel
from ipykernel.kernelbase import Kernel

# Append this files path to sys.path
sys.path.append(os.path.dirname(__file__))

# Import qjide as a module
import qjide

################################################################################
# Global variables
################################################################################

canvasnum = 1

################################################################################
# Jupyter Kernel Class
################################################################################

# Jupyter Kernel Class
class JKernel(Kernel):

   # Basic kernel setup
   implementation         = 'jkernel'
   implementation_version = '2.2.0'
   language_info          = {
      'mimetype':       'text/plain',
      'name':           'J',
      'file_extension': 'ijs'
   }
   banner                 = 'J Programming Language Kernel'
   help_links             = [
      {'text': 'Vocabulary', 'url': 'http://www.jsoftware.com/help/dictionary/vocabul.htm'},
      {'text': 'NuVoc',      'url': 'http://www.jsoftware.com/jwiki/NuVoc'}
   ]

   # Constructor
   def __init__(self, *args, **kwargs):
      # Call super class constructor
      super(JKernel,self).__init__(*args,**kwargs)
      # Initialize J
      self.J = qjide.J(key='main',asn=False)

   # Override do_execute method
   def do_execute(self,code,silent,store_history=True,user_expressions=None,allow_stdin=False):

      # Global variables
      global canvasnum

      # Split cell into single lines
      lines = code.splitlines()

      # Pass input to J
      for line in lines:
         status = self.J.Exec(line)
         # Receive output from J
         output = self.J.Recv()

      # Check silent flag
      if not silent:

         # Check output length
         if len(output) > 0:

            # Check output
            if output.startswith('<!-- j html output a -->'):

               # Error handler
               try:

                  # Is it an image output ?
                  prefix = '<!-- j html output a --><img src="~temp/'
                  if output.startswith(prefix):

                     # Extract image name
                     imgnam = output[len(prefix):]
                     endpos = imgnam.find('?')
                     imgnam = imgnam[:endpos]
                     imgnam = os.path.join(qjide.JInsFol,'user','temp',imgnam)

                     # Read image in base64 encoded data
                     with open(imgnam,'rb') as fp:
                        imgdat = base64.b64encode(fp.read()).decode()
                        #os.remove(imgnam)

                     # Send output data
                     content = {
                        'source': 'J',
                        'data':   {'image/png': imgdat}
                     }
                     self.send_response(self.iopub_socket,'display_data',content)

                  else:

                     # Generate HTML file name
                     htmnam = os.path.join(qjide.JInsFol,'user','temp','plot.html')

                     # Read html file
                     with open(htmnam,'r') as fp:
                        htmdat = fp.read()
                        #os.remove(htmnam)
                        htmdat = htmdat.replace('</article>','</article><script>graph();</script>')
                        htmdat = htmdat.replace('canvas1','canvas' + str(canvasnum))

                        # Increment canvasnum
                        canvasnum += 1

                     content = {
                        'source':   'J',
                        'metadata': { },
                        'data':     {'text/html': htmdat}
                     }
                     self.send_response(self.iopub_socket,'display_data',content)

               except:
                  # Error output
                  content = {
                     'name': 'stdout',
                      'text': 'JKernel: Internal Error.\n' + str(sys.exc_info()[1]) + '\n'
                  }
                  self.send_response(self.iopub_socket,'stream',content)

            else:
               # Normal text output
               content = {
                  'name': 'stdout',
                  'text': output
               }
               self.send_response(self.iopub_socket,'stream',content)

      # Return
      return {
         'status':           'ok',
         'execution_count':  self.execution_count,
         'payload':          [],
         'user_expressions': {},
      }

   # Nothing special here
   def do_shutdown(self,restart):
      pass

   def do_inspect(self,code,cursor_pos,detail_level=0):

      inspection = ""

      code += "\n"
      line = code[code.rfind("\n", 0, cursor_pos)+1 : code.find("\n", cursor_pos)]

      line_pos = cursor_pos - code.rfind("\n", 0, cursor_pos) - 2

      found = False

      if line[line_pos].isalnum():
         i, j = line_pos, line_pos
         while i > 0 and line[i-1].isalnum() or line[i-1] == "_":
            i -= 1
         while j < len(line)-1 and line[j+1].isalnum() or line[j+1] == "_":
            j += 1
         if line[i].isalpha():
            if j == len(line)-1 or line[j+1] not in ".:":
               name = line[i:j+1]
               inspection = self.j.sendline(name)
               found = True

      return {
         'status': 'ok',
         'data': {'text/plain': inspection},
         'metadata': {},
         'found': found
      }

if __name__ == '__main__':
   from ipykernel.kernelapp import IPKernelApp
   IPKernelApp.launch_instance(kernel_class=JKernel)

################################################################################
# EOF
################################################################################
