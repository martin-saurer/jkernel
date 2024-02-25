###############################################################################
#
# File:        setup.py
# Author:      Martin Saurer, 01.01.2018
# Description: Setup script for the J/Jupyter Notebook integration.
#
# License:     GPL Version 3 (see gpl3.txt)
#
###############################################################################

###############################################################################
# Import modules
###############################################################################

import os
import sys
import shutil

###############################################################################
# Utility functions
###############################################################################

# Print exception info
def print_exception_info():
    typ,val,trb = sys.exc_info()
    fil = os.path.split(trb.tb_frame.f_code.co_filename)[1]
    lin = trb.tb_lineno
    est = ('Exception: ' + str(typ) + ': ' + str(val) + ' / in ' + str(fil) +
           ':' + str(lin))
    print(val)

###############################################################################
# Check pre-requisites
###############################################################################

print('')
print('Check pre-requisites ...')

# Get site-packages directory
site_packages_dir = ''
for p in sys.path:
    if p.endswith('site-packages'):
        site_packages_dir = p
        break

# Get anaconda/miniconda root directory
conda_root_dir = os.path.dirname(site_packages_dir)
conda_root_dir = os.path.dirname(conda_root_dir)
if os.name != 'nt':
    conda_root_dir = os.path.dirname(conda_root_dir)

# Build jupyter kernels directory
jupyter_kernels_dir = os.path.join(conda_root_dir     ,'share'  )
jupyter_kernels_dir = os.path.join(jupyter_kernels_dir,'jupyter')
jupyter_kernels_dir = os.path.join(jupyter_kernels_dir,'kernels')

# Build notebook syntax directory
#notebook_syntax_dir = os.path.join(site_packages_dir  ,'notebook'  )
notebook_syntax_dir = os.path.join(site_packages_dir  ,'nbclassic' )
notebook_syntax_dir = os.path.join(notebook_syntax_dir,'static'    )
notebook_syntax_dir = os.path.join(notebook_syntax_dir,'components')
notebook_syntax_dir = os.path.join(notebook_syntax_dir,'codemirror')
notebook_syntax_dir = os.path.join(notebook_syntax_dir,'mode'      )

# Check accessibility
ado = True
if os.access(conda_root_dir,os.W_OK):
    crd = ' OK.'
else:
    crd = ' MISSING or NOT writeable.'
    ado = False
if os.access(site_packages_dir,os.W_OK):
    spd = ' OK.'
else:
    spd = ' MISSING or NOT writeable.'
    ado = False
if os.access(notebook_syntax_dir,os.W_OK):
    nsd = ' OK.'
else:
    nsd = ' MISSING or NOT writeable.'
    ado = False
if os.access(jupyter_kernels_dir,os.W_OK):
    jkd = ' OK.'
else:
    jkd = ' MISSING or NOT writeable.'
    ado = False

# Print directories
print('Anaconda/Miniconda root directory ... : ' + conda_root_dir      + crd)
print('Site Packages directory ............. : ' + site_packages_dir   + spd)
print('Jupyter Notebook syntax directory ... : ' + notebook_syntax_dir + nsd)
print('Jupyter Kernels directory ........... : ' + jupyter_kernels_dir + jkd)

# Print check results
if ado == True:
    print('ALL destination directories are OK.')
    print('Done.')
else:
    print('ERROR: One or more destination directories are not accessible !!!')
    sys.exit(0)

###############################################################################
# Build source files
###############################################################################

src_root_dir = os.path.dirname(sys.argv[0])

src_kernel_dir   = os.path.join(src_root_dir,'jkernel')
src_kernel_files = []
src_kernel_files.append(os.path.join(src_kernel_dir,'__init__.py'))
src_kernel_files.append(os.path.join(src_kernel_dir,'jinter.py'  ))
src_kernel_files.append(os.path.join(src_kernel_dir,'jkernel.py' ))

src_kernel_definition_dir   = os.path.join(src_root_dir,'kernel_definition')
src_kernel_definition_dir   = os.path.join(src_kernel_definition_dir,'jkernel')
src_kernel_definition_files = []
src_kernel_definition_files.append(os.path.join(src_kernel_definition_dir,'kernel.json'))
src_kernel_definition_files.append(os.path.join(src_kernel_definition_dir,'logo-32x32.png'))
src_kernel_definition_files.append(os.path.join(src_kernel_definition_dir,'logo-64x64.png'))

src_syntax_dir   = os.path.join(src_root_dir,'syntax')
src_syntax_dir   = os.path.join(src_syntax_dir,'j')
src_syntax_files = []
src_syntax_files.append(os.path.join(src_syntax_dir,'j.js'))

###############################################################################
# Parse arguments and invoke action
###############################################################################

parm = ''
if len(sys.argv) > 1: parm = sys.argv[1].lower().strip()
mode = ''
if parm == 'install':   mode = parm
if parm == 'uninstall': mode = parm
if parm == 'check':     mode = parm
if mode == '':
    print('')
    print('Usage: setup.py install|uninstall|check')
    print('')
    sys.exit(0)

if sys.argv[1].lower().strip() == 'install':
    print('')
    print('Perform installation ...')
    print('Copy: ' + src_kernel_dir + ' => ' + os.path.join(site_packages_dir,'jkernel'))
    try:
        shutil.copytree(src_kernel_dir,os.path.join(site_packages_dir,'jkernel'))
    except:
        print_exception_info()
    print('Copy: ' + src_kernel_definition_dir + ' => ' + os.path.join(jupyter_kernels_dir,'jkernel'))
    try:
        shutil.copytree(src_kernel_definition_dir,os.path.join(jupyter_kernels_dir,'jkernel'))
    except:
        print_exception_info()
    print('Copy: ' + src_syntax_dir + ' => ' + os.path.join(notebook_syntax_dir,'j'))
    try:
        shutil.copytree(src_syntax_dir,os.path.join(notebook_syntax_dir,'j'))
    except:
        print_exception_info()
    print('Done.')
    print('')
    print('###################################################################')
    print('# PLEASE DO NOT FORGET TO SET THE FOLLOWING ENVIRONMENT VARIABLES #')
    print('#                                                                 #')
    print('# Linux or MacOS: ~/.bashrc or ~/.bash_profile                    #')
    print('# --------------------------------------------                    #')
    print('# export J_INSTALLATION_FOLDER="<J installation folder>"          #')
    print('# export J_BIN_FOLDER="<J binaries folder>"                       #')
    print('#                                                                 #')
    print('# Windows:                                                        #')
    print('# --------                                                        #')
    print('# SET J_INSTALLATION_FOLDER=<J installation folder>               #')
    print('# SET J_BIN_FOLDER=<J binaries folder>                            #')
    print('# ... or via Control Panel ...                                    #')
    print('###################################################################')
    print('')
    sys.exit(0)

if sys.argv[1].lower().strip() == 'uninstall':
    print('')
    print('Perform un-installation ...')
    print('Remove: ' + os.path.join(site_packages_dir,'jkernel'))
    try:
        shutil.rmtree(os.path.join(site_packages_dir,'jkernel'))
    except:
        print_exception_info()
    print('Remove: ' + os.path.join(jupyter_kernels_dir,'jkernel'))
    try:
        shutil.rmtree(os.path.join(jupyter_kernels_dir,'jkernel'))
    except:
        print_exception_info()
    print('Remove: ' + os.path.join(notebook_syntax_dir,'j'))
    try:
        shutil.rmtree(os.path.join(notebook_syntax_dir,'j'))
    except:
        print_exception_info()
    print('Done.')
    sys.exit(0)

if sys.argv[1].lower().strip() == 'check':
    print('')
    print('Checking current installation ...')

    all_ok = True

    pth = os.path.join(site_packages_dir,'jkernel')
    if os.access(pth,os.R_OK):
        print(pth + ' => OK')
    else:
        print(pth + ' => MISSING')
        all_ok = False
    for f in src_kernel_files:
        fn = os.path.basename(f)
        df = os.path.join(pth,fn)
        if os.access(df,os.R_OK):
            print(df + ' => OK')
        else:
            print(df + ' => MISSING')
            all_ok = False

    pth = os.path.join(jupyter_kernels_dir,'jkernel')
    if os.access(pth,os.R_OK):
        print(pth + ' => OK')
    else:
        print(pth + ' => MISSING')
        all_ok = False
    for f in src_kernel_definition_files:
        fn = os.path.basename(f)
        df = os.path.join(pth,fn)
        if os.access(df,os.R_OK):
            print(df + ' => OK')
        else:
            print(df + ' => MISSING')
            all_ok = False

    pth = os.path.join(notebook_syntax_dir,'j')
    if os.access(pth,os.R_OK):
        print(pth + ' => OK')
    else:
        print(pth + ' => MISSING')
        all_ok = False
    for f in src_syntax_files:
        fn = os.path.basename(f)
        df = os.path.join(pth,fn)
        if os.access(df,os.R_OK):
            print(df + ' => OK')
        else:
            print(df + ' => MISSING')
            all_ok = False

    pth = os.getenv('J_INSTALLATION_FOLDER')
    if pth is None: pth = ''
    if pth != '':
        print('Environment variable: J_INSTALLATION_FOLDER => OK')
        if os.access(pth,os.R_OK):
            print(pth + ' => OK')
        else:
            print(pth + ' => MISSING')
            all_ok = False
    else:
        print('Environment variable: J_INSTALLATION_FOLDER => MISSING')
        all_ok = False

    pth = os.getenv('J_BIN_FOLDER')
    if pth is None: pth = ''
    if pth != '':
        print('Environment variable: J_BIN_FOLDER => OK')
        if os.access(pth,os.R_OK):
            print(pth + ' => OK')
        else:
            print(pth + ' => MISSING')
            all_ok = False
    else:
        print('Environment variable: J_BIN_FOLDER => MISSING')
        all_ok = False

    # Print check results
    if all_ok == True:
        print('ALL checks passed.')
        print('Done.')
    else:
        print('ERROR: In one or more of the installation components !!!')

    sys.exit(0)


###############################################################################
# EOF
###############################################################################
