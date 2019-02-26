import sys
import struct
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from RoveComm_Python import *

import threading
import datetime
import time
import os
from XboxController import *

RoveComm = RoveCommEthernetUdp()

types_text_to_byte  = {
						'Int8':'b',
						'uInt8':'B',
						'Int16':'h',
						'uInt16':'H',
						'Int32':'l',
						'uInt32':'L',
					  }
					  
try:
	os.mkdir('0-CSV Outputs')
except:
	pass
	
def controlCallBack(xboxControlId, value):
	print("Control Id = {}, Value = {}".format(xboxControlId, value))
	
controls = ( "Line Entry"
			,"Left Thumb X"
			,"Left Thumb Y"
			,"Right Thumb X"
			,"Right Thumb Y"
			,"D Pad"
			,"L Trigger"
			,"R Trigger"
			,"L Bumper"
			,"R Bumper"
			,"A"
			,"B"
			,"C"
			,"D"
			,"Start")

class Reciever(QWidget):
	
	def __init__(self):
		super().__init__()
		
		self.initUI()
		
	def initUI(self):	
		exitAct = QAction(QIcon('exit.png'), '&Exit', self)        
		exitAct.setShortcut('Ctrl+Q')
		exitAct.setStatusTip('Exit application')
		exitAct.triggered.connect(qApp.quit)
		
		hbox = QHBoxLayout(self)
		
		self.do_thread = True
		
		self.subsciber = Subscriber()
		
		self.logData_cb = QCheckBox("Log Data")
		self.logData_cb.stateChanged.connect(self.logData)
		
		self.autoScroll_cb = QCheckBox("Auto Scroll")
		self.autoScroll_cb.setChecked(True)
		self.start_time = datetime.datetime.now()
		
		
		self.rows = 0
		
		self.recieveTable = QTableWidget()
		self.recieveTable.setColumnCount(7)
		self.recieveTable.setRowCount(self.rows)
		self.recieveTable.setHorizontalHeaderLabels(["Timestamp","Delta T","Data Id","Data Type","Data Count","IP Address","Data"])
		
		self.cbSplitter = QSplitter(Qt.Horizontal)
		self.cbSplitter.addWidget(self.logData_cb)
		self.cbSplitter.addWidget(self.autoScroll_cb)
		
		
		self.splitter1 = QSplitter(Qt.Vertical)
		self.splitter1.addWidget(self.subsciber)
		self.splitter1.addWidget(self.cbSplitter)
		
		self.splitter = QSplitter(Qt.Vertical)
		self.splitter.addWidget(self.splitter1)
		self.splitter.addWidget(self.recieveTable)
		
		hbox.addWidget(self.splitter)
		self.setLayout(hbox)
		
		self.setWindowTitle('Reciever')
		self.setWindowIcon(QIcon('Rover.png')) 
		self.resize(900,500)
		
		self.show()
		
		self.read()
	
	def read(self):
		packet = RoveComm.read()
		if(packet.data_id !=0):
			retrieved_time = datetime.datetime.now()
			elapsed_time = (retrieved_time-self.start_time).total_seconds()
			
			self.recieveTable.setRowCount(self.rows+1)
			
			item = QTableWidgetItem(str(retrieved_time))
			self.recieveTable.setItem(self.rows, 0, item)
			self.recieveTable.setItem(self.rows, 1, QTableWidgetItem(str(elapsed_time)))
			self.recieveTable.setItem(self.rows, 2, QTableWidgetItem(str(packet.data_id)))
			self.recieveTable.setItem(self.rows, 3, QTableWidgetItem(str(packet.data_type)))
			self.recieveTable.setItem(self.rows, 4, QTableWidgetItem(str(packet.data_count)))
			self.recieveTable.setItem(self.rows, 5, QTableWidgetItem(str(packet.ip_address)))
			self.recieveTable.setItem(self.rows, 6, QTableWidgetItem(str(packet.data)))
			self.recieveTable.resizeColumnsToContents()
			
			if(self.autoScroll_cb.isChecked()):
				self.recieveTable.scrollToItem(item)
			
			self.rows = self.rows+1
			
			if(self.logData_cb.isChecked()):
				self.file.write(str(retrieved_time)+','
								+str(elapsed_time)+','
								+str(packet.data_id)+','
								+str(packet.data_type)+','
								+str(packet.data_count)+','
								+str(packet.ip_address)+','
								+str(packet.data)+'\n')
		
		if(self.do_thread):
			threading.Timer(.1, self.read).start()
			
	def logData(self):
		if(self.logData_cb.isChecked()):
			self.start_time = datetime.datetime.now()
			self.file = open('0-CSV Outputs/'+str(self.start_time).replace(':', '_')+'.txt', 'w')
			self.file.write('Time, Delta, Data Id, Data Type, Data Count, Ip Address, Data\n')
		else:
			self.file.close()
	
	def keyPressEvent(self, e):
		if e.key() == Qt.Key_Escape:
			self.close()
			
	def closeEvent(self, event):
		self.do_thread=False
		try:
			self.file.close()
		except:
			pass

class Subscriber(QWidget):
	def __init__(self):
		super().__init__()
		self.initUI()
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
		packet = RoveCommPacket(ROVECOMM_SUBSCRIBE_REQUEST, 'b', (), self.subscribe_octet_4.text())
		RoveComm.write(packet)
		
		
		types_text_to_byte  = {
						'Int8':'b',
						'uInt8':'B',
						'Int16':'h',
						'uInt16':'H',
						'Int32':'l',
						'uInt32':'L',
					  }

class Sender(QWidget):
	
	def __init__(self):
		super().__init__()
		
		self.initUI()
		
	def initUI(self):	
		exitAct = QAction(QIcon('exit.png'), '&Exit', self)        
		exitAct.setShortcut('Ctrl+Q')
		exitAct.setStatusTip('Exit application')
		exitAct.triggered.connect(qApp.quit)
		
		#used with QMainWindow
		#menubar = self.menuBar()
		#fileMenu = menubar.addMenu('&File')
		#fileMenu.addAction(exitAct)
		
		self.send_widgets = [sendWidget(self, 1)]
		
		self.main_layout=QVBoxLayout(self)
		self.main_layout.addWidget(self.send_widgets[0])
		
		self.setWindowTitle('Sender')
		self.setWindowIcon(QIcon('Rover.png')) 
		
		
		self.resize(self.sizeHint())

		self.show()
	def redrawWidgets(self):
		for i in range(0, len(self.send_widgets)):
			self.main_layout.removeWidget(self.send_widgets[i])
			self.main_layout.addWidget(self.send_widgets[i])
			self.send_widgets[i].setNumber(i+1)			
		
	def keyPressEvent(self, e):
		if e.key() == Qt.Key_Escape:
			self.close()
	def addEvent(self, number):
		sender = self.sender()
		self.send_widgets = self.send_widgets[:number] + [sendWidget(self, len(self.send_widgets))] + self.send_widgets[number:]
		self.redrawWidgets()
		
	def removeEvent(self, number):
		sender = self.sender()
		self.main_layout.removeWidget(self.send_widgets[-1])
		self.send_widgets[number-1].deleteLater()
		self.send_widgets[number-1] = None
		self.send_widgets = self.send_widgets[:number-1] + self.send_widgets[number:]
		
		self.redrawWidgets()
		
class sendWidget(QWidget):
	def __init__(self, parent=None, number=1):
		QWidget.__init__(self, parent=parent)
		
		super(sendWidget, self).__init__(parent)
		self.initUI(parent, number)
		
	def initUI(self, parent, number):
		try:
			self.xboxCont = XboxController(controlCallBack, deadzone = 30, scale = 100, invertYAxis = True)
		except:
			pass
			
		self.data_id_text = QLabel('Data ID', self)
		self.data_type_text = QLabel('Data Type', self)
		self.data_size_text = QLabel('Data Size', self)
		self.data_data_text = QLabel('Data', self)
		self.data_input_text = QLabel('Input', self)
		self.data_scalar_text = QLabel('Scalar', self)
		self.data_update_ms_text = QLabel('Update ms', self)
		self.ip_octet_4_text = QLabel('IP Octet 4', self)
		
		self.number_txt = QLabel(str(number) + '.', self)
		self.number = number
		
		send = QPushButton('Send', self)
		send.resize(send.sizeHint())
		send.clicked.connect(self.sendEvent)
		
		add = QPushButton('Add', self)
		add.resize(send.sizeHint())
		add.clicked.connect(self.addEvent)
		
		remove = QPushButton('X', self)
		remove.resize(send.sizeHint())
		remove.clicked.connect(self.removeEvent)
		
		self.data_id_le     = QLineEdit(self)
		self.data_length_le = QLineEdit(self)
		self.ip_octet_4_le  = QLineEdit(self)
		
		self.data_length_le.textChanged[str].connect(self.data_length_entry)
		self.data_length = 1
		
		self.data_type_cb   = QComboBox(self)
		self.data_type_cb.addItem("Int8")
		self.data_type_cb.addItem("uInt8")
		self.data_type_cb.addItem("Int16")
		self.data_type_cb.addItem("uInt16")
		self.data_type_cb.addItem("Int32")
		self.data_type_cb.addItem("uInt32")
		
		self.data_array      = [QLineEdit(self)]
		self.input_cb_array  = [QComboBox(self)]
		self.scalar_array    = [QLineEdit(self)]
		self.update_ms_array = [QLineEdit(self)]
		
		self.input_cb_array[0] = self.addControls(self.input_cb_array[0])
		
		self.main_layout=QGridLayout(self)
		self.main_layout.addWidget(self.data_id_text, 0, 3)
		self.main_layout.addWidget(self.data_type_text, 0, 4)
		self.main_layout.addWidget(self.data_size_text, 0, 5)
		self.main_layout.addWidget(self.data_data_text, 0, 6)
		self.main_layout.addWidget(self.data_input_text, 0, 7)
		self.main_layout.addWidget(self.data_scalar_text, 0, 8)
		self.main_layout.addWidget(self.data_update_ms_text, 0, 9)
		self.main_layout.addWidget(self.ip_octet_4_text, 0, 10)
		
		self.main_layout.addWidget(self.number_txt, 1, 0)
		self.main_layout.addWidget(add, 1, 1)
		self.main_layout.addWidget(remove, 1, 2)
		self.main_layout.addWidget(self.data_id_le, 1, 3)
		self.main_layout.addWidget(self.data_type_cb, 1, 4)
		self.main_layout.addWidget(self.data_length_le, 1, 5)
		self.main_layout.addWidget(self.data_array[0], 1, 6)
		self.main_layout.addWidget(self.input_cb_array[0], 1, 7)
		self.main_layout.addWidget(self.scalar_array[0], 1, 8)
		self.main_layout.addWidget(self.update_ms_array[0], 1, 9)
		self.main_layout.addWidget(self.ip_octet_4_le, 1, 10)
		self.main_layout.addWidget(send, 1, 8)
		self.resize(self.sizeHint())
		
		self.show()
	
	def sendEvent(self):
		data = ( )
		for i in range(0, self.data_length):
			data = (data) + (int(self.data_array[i].text()),)
			
		packet = RoveCommPacket(int(self.data_id_le.text()), types_text_to_byte[self.data_type_cb.currentText()], data, self.ip_octet_4_le.text())
		RoveComm.write(packet)			
	
	def addEvent(self, parent):
		self.parent().addEvent(self.number)
		
	def removeEvent(self, parent):
		self.parent().removeEvent(self.number)
	
	def setNumber(self, number):
		self.number = number
		self.number_txt.setText(str(number) + '.')
	
	def addControls(self, ComboBox):
		for i in controls:
			ComboBox.addItem(i)
		return ComboBox
	
	def data_length_entry(self):
		sender = self.sender()
		try:
			new_length = int(sender.text())
			if(new_length>self.data_length):
				for i in range(self.data_length, new_length):
					self.data_array = self.data_array+[QLineEdit(self)]
					self.main_layout.addWidget(self.data_array[i], i+1, 6)
					
					self.input_cb_array = self.input_cb_array+[QComboBox(self)]
					self.main_layout.addWidget(self.input_cb_array[i], i+1, 7)
					self.input_cb_array[i] = self.addControls(self.input_cb_array[i])
					
					self.scalar_array = self.scalar_array+[QLineEdit(self)]
					self.main_layout.addWidget(self.scalar_array[i], i+1, 8)
					
					self.update_ms_array = self.update_ms_array+[QLineEdit(self)]
					self.main_layout.addWidget(self.update_ms_array[i], i+1, 9)
			elif(new_length<self.data_length):
				for i in range(self.data_length, new_length, -1):
					self.main_layout.removeWidget(self.data_array[-1])
					self.data_array[-1].deleteLater()
					self.data_array[-1] = None
					self.data_array = self.data_array[:-1]
					
					self.main_layout.removeWidget(self.input_cb_array[-1])
					self.input_cb_array[-1].deleteLater()
					self.input_cb_array[-1] = None
					self.input_cb_array = self.input_cb_array[:-1]
					
					self.main_layout.removeWidget(self.scalar_array[-1])
					self.scalar_array[-1].deleteLater()
					self.scalar_array[-1] = None
					self.scalar_array = self.scalar_array[:-1]
					
					self.main_layout.removeWidget(self.update_ms_array[-1])
					self.update_ms_array[-1].deleteLater()
					self.update_ms_array[-1] = None
					self.update_ms_array = self.update_ms_array[:-1]	
			self.data_length = new_length
					
		except:
			return
	
	def keyPressEvent(self, e):
		if e.key() == Qt.Key_Return:
			self.sendEvent()
			
			
if __name__ == '__main__':
	
	app = QApplication(sys.argv)

	ex = Reciever()
	ex.show()
	ex2 = Sender()
	ex2.show()
	
	sys.exit(app.exec())