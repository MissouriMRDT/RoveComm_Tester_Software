'''
pyinstaller --windowed --onedir --icon=rover_1wP_icon.ico RoveComm_Tester.py
'''


import sys
import struct
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from RoveComm_Python import RoveCommPacket, RoveCommEthernetUdp
import json
import images_qr

import threading
import datetime
import time
import os
from XboxController import *

RoveComm = RoveCommEthernetUdp()

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

    ex = Reciever()
    ex.show()
    ex2 = Sender()
    ex2.show()

    sys.exit(app.exec())
