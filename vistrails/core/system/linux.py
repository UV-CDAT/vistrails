############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################
import os
import shutil
from ctypes import CDLL, c_void_p
from core.system.unix import executable_is_in_path,\
     executable_is_in_pythonpath, list2cmdline, execute_cmdline, \
     get_executable_path, execute_piped_cmdlines
import core.bundles

################################################################################

def parse_meminfo():
    """parse_meminfo() -> dictionary
    Parses /proc/meminfo and returns appropriate dictionary. Only available on
    Linux."""
    result = {}
    for line in file('/proc/meminfo'):
        (key, value) = line.split(':')
        value = value[:-1]
        if value.endswith(' kB'):
            value = int(value[:-3]) * 1024
        else:
            try:
                value = int(value)
            except ValueError:
                raise VistrailsInternalError("I was expecting '%s' to be int" 
                                             % value)
        result[key] = value
    return result

def guess_total_memory():
    """ guess_total_memory() -> int 
    Return system memory in bytes. 
    
    """
    return parse_meminfo()['MemTotal']

def temporary_directory():
    """ temporary_directory() -> str 
    Returns the path to the system's temporary directory 
    
    """
    return "/tmp/"

def home_directory():
    """ home_directory() -> str 
    Returns user's home directory using environment variable $HOME
    
    """
    return os.getenv('HOME')

def remote_copy_program():
    return "scp -p"

def remote_shell_program():
    return "ssh -p"

def graph_viz_dot_command_line():
    return 'dot -Tplain -o '

def remove_graph_viz_temporaries():
    """ remove_graph_viz_temporaries() -> None 
    Removes temporary files generated by dot 
    
    """
    os.unlink(temporary_directory() + "dot_output_vistrails.txt")
    os.unlink(temporary_directory() + "dot_tmp_vistrails.txt")

def link_or_copy(src, dst):
    """link_or_copy(src:str, dst:str) -> None 
    Tries to create a hard link to a file. If it is not possible, it will
    copy file src to dst 
    
    """
    # Links if possible, but we're across devices, we need to copy.
    try:
        os.link(src, dst)
    except OSError, e:
        if e.errno == 18:
            # Across-device linking is not possible. Let's copy.
            shutil.copyfile(src, dst)
        else:
            raise e

def get_libX11():
    """ get_libX11() -> CDLL    
    Return the X11 library loaded with ctypes. Only available on
    Linux.  We also need a way to find the correct X11 library name on
    different machines. Right now, libX11.so.6 is used.
    
    """
    ctypes = core.bundles.pyimport.py_import('ctypes',
                                             {'linux-ubuntu':
                                              'python-ctypes'})
    c_void_p = ctypes.c_void_p
    CDLL = ctypes.CDLL
    return CDLL('libX11.so.6')

def XDestroyWindow(displayId, windowId):
    """ XDestroyWindow(displayId: void_p_str, windowId: void_p_str) -> None
    Destroy the X window specified by two strings displayId and
    windowId containing void pointer string of (Display*) and (Window)    
    type.
    This is specific for VTKCell to remove the top shell window. Since
    VTK does not expose X11-related functions to Python, we have to
    use ctypes to hi-jack X11 library and call XDestroyWindow to kill
    the top-shell widget after reparent the OpenGL canvas to another
    Qt widget
    
    """
    ctypes = core.bundles.pyimport.py_import('ctypes',
                                             {'linux-ubuntu':
                                              'python-ctypes'})
    c_void_p = ctypes.c_void_p
    displayPtr = c_void_p(int(displayId[1:displayId.find('_void_p')], 16))
    windowPtr = c_void_p(int(windowId[1:windowId.find('_void_p')], 16))
    libx = get_libX11()
    libx.XDestroyWindow(displayPtr, windowPtr)

################################################################################

import unittest

class TestLinux(unittest.TestCase):
     """ Class to test Linux specific functions """
     
     def test1(self):
         """ Test if guess_total_memory() is returning an int >= 0"""
         result = guess_total_memory()
         assert type(result) == type(1) or type(result) == type(1L)
         assert result >= 0

     def test2(self):
         """ Test if home_directory is not empty """
         result = home_directory()
         assert result != ""

     def test3(self):
         """ Test if temporary_directory is not empty """
         result = temporary_directory()
         assert result != ""

     def test4(self):
         """ Test if origin of link_or_copy'ed file is deleteable. """
         import tempfile
         import os
         (fd1, name1) = tempfile.mkstemp()
         os.close(fd1)
         (fd2, name2) = tempfile.mkstemp()
         os.close(fd2)
         os.unlink(name2)
         link_or_copy(name1, name2)
         try:
             os.unlink(name1)
         except:
             self.fail("Should not throw")
         os.unlink(name2)

     def test_executable_file_in_path(self):
         # Should exist in any POSIX shell, which is what we have in OSX
         result = executable_is_in_path('ls')
         assert result == "/bin/ls" # Any UNIX should respect this.

if __name__ == '__main__':
    unittest.main()
             
