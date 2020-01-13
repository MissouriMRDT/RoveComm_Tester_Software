
import datetime
import threading

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QAction, QHBoxLayout, QLabel, QLineEdit, QCheckBox, QTableWidget, QSplitter, QPushButton, QGridLayout, QTableWidgetItem

from RoveComm_Python import RoveCommPacket, ROVECOMM_SUBSCRIBE_REQUEST


class Reciever(QWidget):

    def __init__(self, qApp, rovecomm):
        super().__init__()

        self.rovecomm = rovecomm
        self.initUI(qApp)

    def initUI(self, qApp):
        exitAct = QAction('&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(qApp.quit)

        hbox = QHBoxLayout(self)

        self.do_thread = True

        self.subsciber = Subscriber(self.rovecomm)

        self.filter_txt = QLabel('Filter:')
        self.filter = QLineEdit()

        self.logData_cb = QCheckBox("Log Data")
        self.logData_cb.stateChanged.connect(self.logData)

        self.autoScroll_cb = QCheckBox("Auto Scroll")
        self.autoScroll_cb.setChecked(True)
        self.start_time = datetime.datetime.now()

        self.rows = 0

        self.recieveTable = QTableWidget()
        self.recieveTable.setColumnCount(7)
        self.recieveTable.setRowCount(self.rows)
        self.recieveTable.setHorizontalHeaderLabels(
            ["Timestamp", "Delta T", "Data Id", "Data Type", "Data Count", "IP Address", "Data"])

        self.cbSplitter = QSplitter(Qt.Horizontal)
        self.cbSplitter.addWidget(self.logData_cb)
        self.cbSplitter.addWidget(self.autoScroll_cb)

        self.filtersplitter = QSplitter(Qt.Horizontal)
        self.filtersplitter.addWidget(self.filter_txt)
        self.filtersplitter.addWidget(self.filter)

        self.controlsSplitter = QSplitter(Qt.Horizontal)
        self.controlsSplitter.addWidget(self.cbSplitter)
        self.controlsSplitter.addWidget(self.filtersplitter)

        self.splitter1 = QSplitter(Qt.Vertical)
        self.splitter1.addWidget(self.subsciber)
        self.splitter1.addWidget(self.controlsSplitter)

        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.addWidget(self.splitter1)
        self.splitter.addWidget(self.recieveTable)

        hbox.addWidget(self.splitter)
        self.setLayout(hbox)

        self.setWindowTitle('Reciever')
        # self.setWindowIcon(QIcon(':/Rover.png'))
        self.resize(900, 500)

        self.show()

        self.read()

    def read(self):
        packet = self.rovecomm.read()
        if(packet.data_id != 0):
            print(self.filter.text)
            if(self.filter.text() == "" or int(self.filter.text()) == packet.data_id):
                retrieved_time = datetime.datetime.now()
                elapsed_time = (retrieved_time-self.start_time).total_seconds()

                self.recieveTable.setRowCount(self.rows+1)

                item = QTableWidgetItem(str(retrieved_time))
                self.recieveTable.setItem(self.rows, 0, item)
                self.recieveTable.setItem(
                    self.rows, 1, QTableWidgetItem(str(elapsed_time)))
                self.recieveTable.setItem(
                    self.rows, 2, QTableWidgetItem(str(packet.data_id)))
                self.recieveTable.setItem(
                    self.rows, 3, QTableWidgetItem(str(packet.data_type)))
                self.recieveTable.setItem(
                    self.rows, 4, QTableWidgetItem(str(packet.data_count)))
                self.recieveTable.setItem(
                    self.rows, 5, QTableWidgetItem(str(packet.ip_address)))
                self.recieveTable.setItem(
                    self.rows, 6, QTableWidgetItem(str(packet.data)))
                self.recieveTable.resizeColumnsToContents()

                if(self.autoScroll_cb.isChecked()):
                    self.recieveTable.scrollToItem(item)

                self.rows = self.rows+1

                if(self.logData_cb.isChecked()):
                    self.file.write(str(retrieved_time)+','
                                    + str(elapsed_time)+','
                                    + str(packet.data_id)+','
                                    + str(packet.data_type)+','
                                    + str(packet.data_count)+','
                                    + str(packet.ip_address)+','
                                    + str(packet.data)+'\n')

        if(self.do_thread):
            threading.Timer(.1, self.read).start()

    def logData(self):
        if(self.logData_cb.isChecked()):
            self.start_time = datetime.datetime.now()
            self.file = open(
                '0-CSV Outputs/'+str(self.start_time).replace(':', '_')+'.txt', 'w')
            self.file.write(
                'Time, Delta, Data Id, Data Type, Data Count, Ip Address, Data\n')
        else:
            self.file.close()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

    def closeEvent(self, event):
        self.do_thread = False
        try:
            self.file.close()
        except:
            pass


class Subscriber(QWidget):
    def __init__(self, rovecomm):
        super().__init__()
        self.initUI()
        self.rovecomm = rovecomm

    def initUI(self):
        self.subscribe_txt = QLabel('Subscribe To Octet 4:')

        self.subscribe_octet_4 = QLineEdit()

        self.subscribe_pb = QPushButton('Subscribe', self)
        self.subscribe_pb.clicked.connect(self.subscribeEvent)

        self.main_layout = QGridLayout(self)
        self.main_layout.addWidget(self.subscribe_txt, 0, 0)
        self.main_layout.addWidget(self.subscribe_octet_4, 0, 1)
        self.main_layout.addWidget(self.subscribe_pb, 0, 2)

        self.show()

    def subscribeEvent(self):
        packet = RoveCommPacket(
            ROVECOMM_SUBSCRIBE_REQUEST, 'b', (), self.subscribe_octet_4.text())
        self.rovecomm.write(packet)
