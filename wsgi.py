import sys
path = '/home/MidnightMelancholia/Messenger'
if path not in sys.path:
   sys.path.insert(0, path)

from app import app as application