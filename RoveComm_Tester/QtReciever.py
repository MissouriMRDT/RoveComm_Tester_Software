import datetime
import threading
import time

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QWidget,
    QAction,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QCheckBox,
    QTableWidget,
    QSplitter,
    QPushButton,
    QGridLayout,
    QTableWidgetItem,
)

from rovecomm_module.rovecomm import RoveCommPacket, ROVECOMM_SUBSCRIBE_REQUEST


# Class for window that allows a user to:
# -Subscribe to devices on a network
# -Read packets that those devices send
class Reciever(QWidget):
    def __init__(self, qApp, rovecommUdp, rovecommTCP):
        super().__init__()

        # Instance from main that instantiated this
        self.rovecommUdp = rovecommUdp
        self.rovecommTCP = rovecommTCP

        exitAct = QAction("&Exit", self)
        exitAct.setShortcut("Ctrl+Q")
        exitAct.setStatusTip("Exit application")
        exitAct.triggered.connect(qApp.quit)

        # Thread control boolean, for when closing
        self.do_thread = True

        # Subsciber gui instance
        self.subsciber_gui = Subscriber(self.rovecommUdp, self.rovecommTCP)

        # Packet contents filter
        self.filter_txt = QLabel("Filter:")
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
            ["Timestamp", "Delta T", "IP Address", "Data Id", "Data Type", "Data Count", "Data"]
        )

        # Log data, auto scroll, and filter controls row layout definition
        self.controls_hbox = QHBoxLayout()
        self.controls_hbox.addWidget(self.logData_cb)
        self.controls_hbox.addWidget(self.autoScroll_cb)
        self.controls_hbox.addWidget(self.filter_txt)
        self.controls_hbox.addWidget(self.filter)

        # Adding elements to main layout
        layout_vbox = QVBoxLayout(self)
        layout_vbox.addWidget(self.subsciber_gui)
        layout_vbox.addLayout(self.controls_hbox)
        layout_vbox.addWidget(self.recieveTable)

        self.setLayout(layout_vbox)
        self.setWindowTitle("Reciever")
        self.setWindowIcon(QIcon("rover_swoosh.ico"))
        self.resize(900, 500)

        self.show()

        # start a seperate thread for rovecomm reading
        self.read_thread = threading.Thread(target=self.read)
        # start the thread
        self.read_thread.start()

    # Loop for recieving packets
    def read(self):
        while self.do_thread:
            packets = []

            # Thread here holds until packet arrives
            packets.append(self.rovecommUdp.read())

            # also check for any incoming packets for any of the ongoing TCP connections
            tcp_packets = self.rovecommTCP.read()
            for packet in tcp_packets:
                packets.append(packet)

            for packet in packets:
                if packet != None and packet.data_id != 0:
                    if self.passesFilter(packet):
                        retrieved_time = datetime.datetime.now()
                        elapsed_time = (retrieved_time - self.start_time).total_seconds()

                        self.addDataRow(packet, retrieved_time, elapsed_time)

                        if self.logData_cb.isChecked():
                            self.logData(packet, retrieved_time, elapsed_time)
            time.sleep(0.01)

    # Insert new data into display table
    def addDataRow(self, packet, retrieved_time, elapsed_time):
        self.recieveTable.setRowCount(self.row_count + 1)

        self.recieveTable.setItem(self.row_count, 0, QTableWidgetItem(str(retrieved_time)))
        self.recieveTable.setItem(self.row_count, 1, QTableWidgetItem(str(elapsed_time)))
        self.recieveTable.setItem(self.row_count, 2, QTableWidgetItem(str(packet.ip_address)))
        self.recieveTable.setItem(self.row_count, 3, QTableWidgetItem(str(packet.data_id)))
        self.recieveTable.setItem(self.row_count, 4, QTableWidgetItem(str(packet.data_type)))
        self.recieveTable.setItem(self.row_count, 5, QTableWidgetItem(str(packet.data_count)))
        self.recieveTable.setItem(self.row_count, 6, QTableWidgetItem(str(packet.data)))
        self.recieveTable.resizeColumnsToContents()

        if self.autoScroll_cb.isChecked():
            self.recieveTable.scrollToItem(self.recieveTable.item(self.row_count, 0))

        self.row_count = self.row_count + 1

    # Handler for the logging checkbox
    def logFileHandler(self):
        if self.logData_cb.isChecked():
            self.start_time = datetime.datetime.now()
            self.file = open("0-CSV Outputs/" + str(self.start_time).replace(":", "_") + ".csv", "w")
            self.file.write('Time,Delta,"IP Address",Port,"Data Id","Data Type","Data Count",Data\n')
        else:
            self.file.close()

    # Log a packet to the open file
    def logData(self, packet, retrieved_time, elapsed_time):
        self.file.write(
            '"'
            + str(retrieved_time)
            + '",'
            + str(elapsed_time)
            + ","
            + str(packet.address[0])
            + ","
            + str(packet.address[1])
            + ","
            + str(packet.data_id)
            + ","
            + str(packet.data_type)
            + ","
            + str(packet.data_count)
            + ',"'
            + str(packet.data)
            + '"\n'
        )

    # Test to determine if packet qualifies under the text filter
    def passesFilter(self, packet):
        try:
            return (
                self.filter.text() == ""
                or self.filter.text() in str(packet.ip_address[0])
                or self.filter.text() == packet.data_type
                or self.filter.text() in str(packet.data)
                or int(self.filter.text()) == packet.data_id
            )
        except:
            return False

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

    def closeEvent(self, event):
        self.do_thread = False
        self.read_thread.join()
        try:
            self.file.close()
        except:
            pass


# Defines subscriber control widget
class Subscriber(QWidget):
    def __init__(self, rovecommUdp, rovecommTCP):
        super().__init__()
        self.rovecommUdp = rovecommUdp
        self.rovecommTCP = rovecommTCP

        self.octet_input_udp = QLineEdit()
        self.octet_input_tcp = QLineEdit()
        self.port_input_tcp = QLineEdit()

        self.subscribe_pb_udp = QPushButton("Subscribe (UDP)", self)
        self.subscribe_pb_udp.clicked.connect(self.subscribeEventUdp)
        self.subscribe_pb_tcp = QPushButton("Subscribe (TCP) ", self)
        self.subscribe_pb_tcp.clicked.connect(self.subscribeEventTCP)

        self.main_layout = QVBoxLayout()
        self.UDP_subscribe = QHBoxLayout()
        self.TCP_subscribe = QHBoxLayout()
        self.UDP_subscribe.addWidget(QLabel("Subscribe to IP:"))
        self.UDP_subscribe.addWidget(self.octet_input_udp)
        self.UDP_subscribe.addWidget(self.subscribe_pb_udp)
        self.main_layout.addLayout(self.UDP_subscribe)
        self.TCP_subscribe.addWidget(QLabel("Subscribe to IP:"))
        self.TCP_subscribe.addWidget(self.octet_input_tcp)
        self.TCP_subscribe.addWidget(QLabel("Port Number:"))
        self.TCP_subscribe.addWidget(self.port_input_tcp)
        self.TCP_subscribe.addWidget(self.subscribe_pb_tcp)
        self.main_layout.addLayout(self.TCP_subscribe)
        self.setLayout(self.main_layout)
        self.show()

    def subscribeEventUdp(self):
        packet = RoveCommPacket(ROVECOMM_SUBSCRIBE_REQUEST, "b", (), self.octet_input_udp.text())
        self.rovecommUdp.write(packet)

    def subscribeEventTCP(self):
        self.rovecommTCP.connect((self.octet_input_tcp.text(), int(self.port_input_tcp.text())))
