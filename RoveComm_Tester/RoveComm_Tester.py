
import os
import sys

from PyQt5.QtWidgets import QApplication

from RoveComm_Python import RoveCommPacket, RoveCommEthernetUdp, RoveCommEthernetTCP

from QtReciever import Reciever
from QtSender import Sender


if __name__ == '__main__':

    rovecommUdp = RoveCommEthernetUdp()
    rovecommTCP = RoveCommEthernetTCP()

    try:
        os.mkdir('0-CSV Outputs')
    except:
        pass

    try:
        os.mkdir('1-Configs')
    except:
        pass

    app = QApplication(sys.argv)

    ex = Reciever(app, rovecommUdp, rovecommTCP)
    ex.show()
    ex2 = Sender(app, rovecommUdp, rovecommTCP)
    ex2.show()

    sys.exit(app.exec())
