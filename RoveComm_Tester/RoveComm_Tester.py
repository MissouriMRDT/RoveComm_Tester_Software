
import os
import sys

from PyQt5.QtWidgets import QApplication

from RoveComm_Python import RoveCommEthernetUdp

from QtReciever import Reciever
from QtSender import Sender


if __name__ == '__main__':

    rovecomm = RoveCommEthernetUdp()

    try:
        os.mkdir('0-CSV Outputs')
    except:
        pass

    try:
        os.mkdir('1-Configs')
    except:
        pass

    app = QApplication(sys.argv)

    ex = Reciever(app, rovecomm)
    ex.show()
    ex2 = Sender(app, rovecomm)
    ex2.show()

    sys.exit(app.exec())
