import sys
import struct
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from RoveComm_Python import *

RoveComm = RoveCommEthernetUdp()

class Example(QWidget):
	
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
		
		send1 = sendWidget(self)
		send2 = sendWidget(self)
		
		self.setWindowTitle('RoveComm App')
		self.setWindowIcon(QIcon('Rover.png')) 
		self.resize(200, 300)
		
		self.layout = QHBoxLayout()
		self.layout.addWidget(send1)
		self.layout.addWidget(send2)

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
		send.move(0,200)  
		send.clicked.connect(self.sendEvent)
		
		recieve = QPushButton('Recieve', self)
		recieve.resize(send.sizeHint())
		recieve.move(100,200)  
		recieve.clicked.connect(self.recieveEvent)
		
		self.data_id_le = QLineEdit(self)
		self.data_id_le.move(0, 50)
		
		self.data_size_le = QLineEdit(self)
		self.data_size_le.move(0, 100)
		
		self.data_data_le = QLineEdit(self)
		self.data_data_le.move(0, 150)
		
		self.layout=QVBoxLayout(self)
		self.layout.addWidget(self.data_id_le)
		self.layout.addWidget(self.data_size_le)
		self.layout.addWidget(self.data_data_le)
		self.layout.addWidget(send)
		self.layout.addWidget(recieve)
		#self.show()
		
	def sendEvent(self):
		RoveComm.writeTo(int(self.data_id_le.text()), int(self.data_size_le.text()), struct.pack('>L', int(self.data_data_le.text())), '127.0.0.1')
		print(self.data_id_le.text(), self.data_size_le.text(), self.data_data_le.text())
		
	def recieveEvent(self):
		data_id, data_size, data = RoveComm.read()
		print(data_id, data_size, struct.unpack('>L', data))		
		
if __name__ == '__main__':
	
	app = QApplication(sys.argv)
	ex = Example()
	sys.exit(app.exec_())