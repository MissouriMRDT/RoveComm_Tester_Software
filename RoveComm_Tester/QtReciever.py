
import datetime
import threading

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QAction, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QCheckBox, QTableWidget, QSplitter, QPushButton, QGridLayout, QTableWidgetItem

from RoveComm_Python import RoveCommPacket, ROVECOMM_SUBSCRIBE_REQUEST


# Class for window that allows a user to:
# -Subscribe to devices on a network
# -Read packets that those devices send
class Reciever(QWidget):

    def __init__(self, qApp, rovecomm):
        super().__init__()

        # Instance from main that instantiated this
        self.rovecomm = rovecomm

        exitAct = QAction('&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(qApp.quit)

        # Thread control boolean, for when closing
        self.do_thread = True

        # Subsciber gui instance
        self.subsciber_gui = Subscriber(self.rovecomm)

        # Packet contents filter
        self.filter_txt = QLabel('Filter:')
        self.filter = QLineEdit()

        # Checkbox to control logging data to local csv file
        self.logData_cb = QCheckBox("Log Data")
        self.logData_cb.stateChanged.connect(self.logFileHandler)
        self.start_time = datetime.datetime.now()

        # Control for table scrolling
        self.autoScroll_cb = QCheckBox("Auto Scroll")
        self.autoScroll_cb.setChecked(True)


        self.row_count = 0

        # Table for incoming packets, column definitions
        self.recieveTable = QTableWidget()
        self.recieveTable.setColumnCount(7)
        self.recieveTable.setRowCount(self.row_count)
        self.recieveTable.setHorizontalHeaderLabels(
            ["Timestamp", "Delta T", "Data Id", "Data Type", "Data Count", "IP Address", "Data"])

        # Log data, auto scroll, and filter controls row layout definition
        self.controls_hbox = QHBoxLayout(self)
        self.controls_hbox.addWidget(self.logData_cb)
        self.controls_hbox.addWidget(self.autoScroll_cb)
        self.controls_hbox.addWidget(self.filter_txt)
        self.controls_hbox.addWidget(self.filter)

        # Adding elements to main layout
        layout_vbox = QVBoxLayout(self)
        layout_vbox.addLayout(self.controls_hbox)
        layout_vbox.addWidget(self.subsciber_gui)
        layout_vbox.addWidget(self.recieveTable)

        self.setLayout(layout_vbox)
        self.setWindowTitle('Reciever')
        # self.setWindowIcon(QIcon(':/Rover.png'))
        self.resize(900, 500)

        self.show()

        self.read()


    # Loop for recieving packets
    def read(self):

        # Thread here holds until packet arrives
        packet = self.rovecomm.read()

        if(packet.data_id != 0):
            if(self.passesFilter(packet)):
                retrieved_time = datetime.datetime.now()
                elapsed_time = (retrieved_time-self.start_time).total_seconds()

                self.addDataRow(packet, retrieved_time, elapsed_time)

                if(self.logData_cb.isChecked()):
                    self.logData(packet, retrieved_time, elapsed_time)

        # Call this method repeatedly
        if(self.do_thread):
            threading.Timer(.01, self.read).start()


    # Insert new data into display table
    def addDataRow(self, packet, retrieved_time, elapsed_time):
        self.recieveTable.setRowCount(self.row_count+1)

        self.recieveTable.setItem(
            self.row_count, 0, QTableWidgetItem(str(retrieved_time)))
        self.recieveTable.setItem(
            self.row_count, 1, QTableWidgetItem(str(elapsed_time)))
        self.recieveTable.setItem(
            self.row_count, 2, QTableWidgetItem(str(packet.data_id)))
        self.recieveTable.setItem(
            self.row_count, 3, QTableWidgetItem(str(packet.data_type)))
        self.recieveTable.setItem(
            self.row_count, 4, QTableWidgetItem(str(packet.data_count)))
        self.recieveTable.setItem(
            self.row_count, 5, QTableWidgetItem(str(packet.ip_address)))
        self.recieveTable.setItem(
            self.row_count, 6, QTableWidgetItem(str(packet.data)))
        self.recieveTable.resizeColumnsToContents()

        if(self.autoScroll_cb.isChecked()):
                    self.recieveTable.scrollToItem(
                        self.recieveTable.itemAt(self.row_count, 0))

        self.row_count = self.row_count+1


    # Handler for the logging checkbox
    def logFileHandler(self):
        if(self.logData_cb.isChecked()):
            self.start_time = datetime.datetime.now()
            self.file = open(
                '0-CSV Outputs/'+str(self.start_time).replace(':', '_')+'.csv', 'w')
            self.file.write(
                'Time, Delta, Data Id, Data Type, Data Count, Ip Address, Data\n')
        else:
            self.file.close()


    # Log a packet to the open file
    def logData(self, packet, retrieved_time, elapsed_time):
        self.file.write(str(retrieved_time)+','
                        + str(elapsed_time)+','
                        + str(packet.data_id)+','
                        + str(packet.data_type)+','
                        + str(packet.data_count)+','
                        + str(packet.ip_address)+','
                        + str(packet.data)+'\n')


    # Test to determine if packet qualifies under the text filter
    def passesFilter(self, packet):
        return (self.filter.text() == "" or
                int(self.filter.text()) == packet.data_id or
                self.filter.text() == packet.data_type or
                self.filter.text() in str(packet.ip_address[0]) or
                self.filter.text() in str(packet.data))


    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()


    def closeEvent(self, event):
        self.do_thread = False
        try:
            self.file.close()
        except:
            pass


# Defines subscriber control widget
class Subscriber(QWidget):
    def __init__(self, rovecomm):
        super().__init__()
        self.rovecomm = rovecomm

        self.octet_input = QLineEdit()

        self.subscribe_pb = QPushButton('Subscribe', self)
        self.subscribe_pb.clicked.connect(self.subscribeEvent)

        self.main_layout = QHBoxLayout(self)
        self.main_layout.addWidget(QLabel('Subscribe To Octet 4:'))
        self.main_layout.addWidget(self.octet_input)
        self.main_layout.addWidget(self.subscribe_pb)

        self.show()

    def subscribeEvent(self):
        packet = RoveCommPacket(
            ROVECOMM_SUBSCRIBE_REQUEST, 'b', (), self.octet_input.text())
        self.rovecomm.write(packet)
