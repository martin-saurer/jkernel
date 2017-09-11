# jkernel

The jkernel is a Jupyter Notebook / J Integration.

It is based on the same code as [qjide](http://www.github.com/martin-saurer/qjide).

## Prerequisites

* [Jupyter Notebook](http://jupyter.org) Version 4.0.6 (or greater). Recommended: [Anaconda from Continuum Analytics](https://www.continuum.io/downloads)

* A working [J 804](http://www.jsoftware.com) installation

## Installation

### Kernel

Copy the directory "jkernel" to your anaconda installation folder:

* Mac OS X: \<anaconda-installation-folder\>/lib/python3.5/site-packages/

* Linux: \<anaconda-installation-folder\>/lib/python3.5/site-packages/

* Windows: \<anaconda-installation-folder\>\\Lib\\site-packages\\

### Kernel Configuration

* Edit qjide.cfg to specify your J installation folder

* Edit qjide.cfg to specify your J binaries folder, especially on Arch Linux, where libj.so goes to /usr/lib/j8/bin

### Kernel Definition

Copy the directory "jkernel" under \<repository\>/kernel_definition/ to:

* Mac OS X: \<anaconda-installation-folder\>/share/jupyter/kernels/

* Linux: \<anaconda-installation-folder\>/share/jupyter/kernels/

* Windows: \<anaconda-installation-folder\>\\share\\jupyter\\kernels\\

### Syntax Highlighting

Copy the file "J.js" under \<repository\>/syntax/ to:

* Mac OS X: \<anaconda-installation-folder\>/lib/python3.5/site-packages/notebook/static/components/codemirror/mode/J/J.js


* Linux: \<anaconda-installation-folder\>/lib/python3.5/site-packages/notebook/static/components/codemirror/mode/J/J.js


* Windows: \<anaconda-installation-folder\>\\Lib\\site-packages\\notebook\\static\\components\\codemirror\\mode\\J\\J.js

### Examples

The sub-directory examples contains some examples using Jupyter Notebook with the jkernel.

You may copy the .ipynb files to any location you wish.

Plase copy the sub-directory jupyter_examples to your J user folder.

## Run

Run: **jupyter notebook** (from the command line)

Or: Use the anaconda launcher, and start "ipython-notebook"
