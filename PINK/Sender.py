import sys
import struct
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from RoveComm_Python import *

RoveComm = RoveCommEthernetUdp()

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
		
		self.data_id_text = QLabel('Data ID', self)
		self.data_id_text.move(50, 0)
		
		self.data_size_text = QLabel('Data Size', self)
		self.data_size_text.move(200, 0)
		
		self.data_data_text = QLabel('Data', self)
		self.data_data_text.move(350, 0)
		
		self.ip_octet_4_text = QLabel('IP Octet 4', self)
		self.ip_octet_4_text.move(500, 0)
		
		self.send1 = sendWidget(self)
		self.send1.move(0, 10)
		
		self.send2 = sendWidget(self)
		self.send2.move(0, 40)
		
		self.setWindowTitle('Sender')
		self.setWindowIcon(QIcon('Rover.png')) 
		self.resize(600, 120)

		self.show()
		
	def keyPressEvent(self, e):
		if e.key() == Qt.Key_Escape:
			self.close()
		
class sendWidget(QWidget):
	def __init__(self, parent=None):
		QWidget.__init__(self, parent=parent)
		
		self.initUI()
		
	def initUI(self):
		send = QPushButton('Send', self)
		send.resize(send.sizeHint())
		send.clicked.connect(self.sendEvent)
		
		self.data_id_le    = QLineEdit(self)
		self.data_size_le  = QLineEdit(self)
		self.data_data_le  = QLineEdit(self)
		self.ip_octet_4_le = QLineEdit(self)
		
		layout=QHBoxLayout(self)
		layout.addWidget(self.data_id_le)
		layout.addWidget(self.data_size_le)
		layout.addWidget(self.data_data_le)
		layout.addWidget(self.ip_octet_4_le)
		layout.addWidget(send)

		
	def sendEvent(self):
		RoveComm.writeTo(int(self.data_id_le.text()), int(self.data_size_le.text()), struct.pack('>L', int(self.data_data_le.text())), '192.168.1.'+ self.ip_octet_4_le.text())
		print(self.data_id_le.text(), self.data_size_le.text(), self.data_data_le.text(), '192.168.1.'+ self.ip_octet_4_le.text())		
		
if __name__ == '__main__':
	
	app = QApplication(sys.argv)
	ex = Sender()
	sys.exit(app.exec_())