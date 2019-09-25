import os
from shutil import rmtree

CACHE = '__pycache__'

def CleanPyCache(current='.'):
  dirs = next(os.walk(current))[1]
  if CACHE in dirs:
    rmtree(os.path.join(current, CACHE))
  for subdir in dirs:
    if subdir == CACHE: continue
    CleanPyCache(os.path.join(current, subdir))

def ifnmkdir(d):
  try: os.mkdir(d)
  except FileExistsError: pass
