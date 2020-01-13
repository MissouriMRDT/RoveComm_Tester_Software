'''
pyinstaller --windowed --onedir --icon=rover_1wP_icon.ico RoveComm_Tester.py
'''


#import struct
#from PyQt5.QtCore import *
#from PyQt5.QtWidgets import *
#from PyQt5.QtGui import *
#import json
#import images_qr

#import threading
#import datetime
#import time
#from XboxController import *


import os
import sys

from PyQt5.QtWidgets import QApplication

from RoveComm_Python import RoveCommPacket, RoveCommEthernetUdp

from QtReciever import Reciever
from QtSender import Sender


rovecomm = RoveCommEthernetUdp()

try:
    os.mkdir('0-CSV Outputs')
except:
    pass

try:
    os.mkdir('1-Configs')
except:
    pass


if __name__ == '__main__':

    app = QApplication(sys.argv)

    ex = Reciever(app, rovecomm)
    ex.show()
    ex2 = Sender(app, rovecomm)
    ex2.show()

    sys.exit(app.exec())
