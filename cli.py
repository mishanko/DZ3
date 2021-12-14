## для команд для шела
from config import HOST, PORT
from app import application
import sys
import os

def start():
    application.run(host=HOST, port=PORT)

if __name__ == '__main__':
    sys.path.insert(0, os.path.abspath(os.getcwd()))
    start()