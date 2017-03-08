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
    import json, math, sys, os, io, ast, unicodedata, hashlib, re, random, time, warnings, datetime as dt, logging as lg
    from collections import OrderedDict, Counter
    from itertools import groupby, chain
    from dateutil import parser as date_parser
    import requests, numpy as np, pandas as pd, geopandas as gpd
    from shapely.geometry import Polygon


def connect_to_mapi():
    pass




