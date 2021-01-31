import os
import sys
import json

from PyQt5.QtWidgets import QApplication
from RoveComm_Python import RoveCommPacket, RoveCommEthernetUdp, RoveCommEthernetTCP
from QtReciever import Reciever
from QtSender import Sender


if __name__ == "__main__":

    config = open("config.json", "r").read()
    config = json.loads(config)

    rovecommUdp = RoveCommEthernetUdp(port=config["UDP_PORT"])
    rovecommTCP = RoveCommEthernetTCP(PORT=config["TCP_PORT"])

    try:
        os.mkdir("0-CSV Outputs")
    except:
        pass

    try:
        os.mkdir("1-Configs")
    except:
        pass

    app = QApplication(sys.argv)

    ex = Reciever(app, rovecommUdp, rovecommTCP)
    ex.show()
    ex2 = Sender(app, rovecommUdp, rovecommTCP)
    ex2.show()

    ret = app.exec_()

    # clean up our sockets before we terminate
    rovecommTCP.close_sockets()

    sys.exit(ret)
