import sys
import os

# Voeg de root directory toe zodat server.py gevonden wordt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import app
