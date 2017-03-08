"""
opentaba gushim tests
-----------
"""

import os
import shutil

if os.path.exists('.temp'):
    shutil.rmtree('.temp')

import gushim as gs, logging as lg

gs.config(workspace_folder='.temp/data', log_console=True, log_file=True, log_folder='.logs')

gs.log('test debug', level=lg.DEBUG)
gs.log('test info', level=lg.INFO)
gs.log('test warning', level=lg.WARNING)
gs.log('test error', level=lg.ERROR)


def test_imports():
    pass
    
