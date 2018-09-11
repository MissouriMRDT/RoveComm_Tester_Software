import sys
import struct
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from RoveComm_Python import *

RoveComm = RoveCommEthernetUdp()

class Reciever(QWidget):
	
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
		
		self.recieve1 = sendWidget(self)
		self.recieve1.move(0, 10)
		
		self.recieve2 = sendWidget(self)
		self.recieve2.move(0, 40)
		
		self.setWindowTitle('Reciever')
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
		recieve = QPushButton('Recieve', self)
		recieve.resize(recieve.sizeHint())
		recieve.clicked.connect(self.recieveEvent)
		
		self.data_id_le = QLineEdit(self)
		self.data_size_le = QLineEdit(self)
		self.data_data_le = QLineEdit(self)
		
		self.recieve_tag = QLabel('           ')
		
		layout=QHBoxLayout(self)
		layout.addWidget(self.data_id_le)
		layout.addWidget(self.data_size_le)
		layout.addWidget(self.data_data_le)
		layout.addWidget(recieve)
		layout.addWidget(self.recieve_tag)
		
	def recieveEvent(self):

		data_id, data_size, data = RoveComm.read()
		if (str(data_id) == self.data_id_le.text()):
			self.data_size_le.setText(str(data_size))
			#self.data_data_le.setText(str(struct.unpack('>L', data)))
			self.recieve_tag.setText('Success')
		else:
			self.recieve_tag.setText('Fail      ')
		#print(data_id, data_size, struct.unpack('>L', data))		
		
if __name__ == '__main__':
	
	app = QApplication(sys.argv)
	ex = Reciever()
	sys.exit(app.exec_())