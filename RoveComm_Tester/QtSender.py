

controls = ("Line Entry", "Left Thumb X", "Left Thumb Y", "Right Thumb X", "Right Thumb Y", "D Pad X", "D Pad Y",
            "L Trigger", "R Trigger", "L Bumper", "R Bumper", "A", "B", "X", "Y", "Back", "Start", "L Thumb", "R Thumb")

data_types = {
    'Int8': 'b',
    'uInt8': 'B',
    'Int16': 'h',
    'uInt16': 'H',
    'Int32': 'l',
    'uInt32': 'L'
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

        # used with QMainWindow
        #menubar = self.menuBar()
        #fileMenu = menubar.addMenu('&File')
        # fileMenu.addAction(exitAct)

        self.loadJson_pb = QPushButton("Load Configs")
        self.loadJson_pb.clicked.connect(self.loadJSON)

        self.writeJson_pb = QPushButton("Write Config")
        self.writeJson_pb.clicked.connect(self.writeJSON)

        self.splitter = QSplitter()
        self.splitter.addWidget(self.loadJson_pb)
        self.splitter.addWidget(self.writeJson_pb)

        self.send_widgets = [sendWidget(self, 1)]

        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.splitter)
        self.main_layout.addWidget(self.send_widgets[0])

        self.setWindowTitle('Sender')
        self.setWindowIcon(QIcon(':/Rover.png'))

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
        self.send_widgets = self.send_widgets[:number] + [sendWidget(
            self, len(self.send_widgets))] + self.send_widgets[number:]
        self.redrawWidgets()

    def removeEvent(self, number):
        sender = self.sender()
        self.main_layout.removeWidget(self.send_widgets[-1])
        self.send_widgets[number-1].close()
        self.send_widgets[number-1].deleteLater()
        self.send_widgets[number-1] = None
        self.send_widgets = self.send_widgets[:number -
                                              1] + self.send_widgets[number:]

        self.redrawWidgets()

    def loadJSON(self):
        try:
            load_files = QFileDialog.getOpenFileNames(
                QFileDialog(), filter="JSON(*.json)", directory="1-Configs/")
            print(load_files)
            for k in range(0, len(load_files)):
                data = json.loads(open(load_files[0][k]).read())
                start_number = len(self.send_widgets)
                for i in range(0, int(data["packet_count"])):
                    try:
                        self.addEvent(start_number+i)
                        self.send_widgets[start_number +
                                          i].data_id_le.setText(data["packet"][i]["data_id"])
                        self.send_widgets[start_number +
                                          i].update_ms_le.setText(data["packet"][i]["update_ms"])
                        self.send_widgets[start_number+i].ip_octet_4_le.setText(
                            data["packet"][i]["ip_octet_4"])
                        self.send_widgets[start_number+i].data_type_cb.setCurrentText(
                            data["packet"][i]["data_type"])

                        data_size = int(data["packet"][i]["data_size"])
                        self.send_widgets[start_number +
                                          i].data_length_le.setText(str(data_size))
                        for j in range(0, data_size):
                            self.send_widgets[start_number+i].data_array[j].setText(
                                data["packet"][i]["data"][j]["data"])
                            self.send_widgets[start_number+i].scalar_array[j].setText(
                                data["packet"][i]["data"][j]["scalar"])
                            self.send_widgets[start_number+i].input_cb_array[j].setCurrentText(
                                data["packet"][i]["data"][j]["input"])
                    except:
                        pass
        except:
            pass

    def writeJSON(self):
        data = {
            "packet_count": len(self.send_widgets)
        }
        data["packet"] = []

        for i in range(0, len(self.send_widgets)):
            try:
                data["packet"].append({})
                data["packet"][i]["data_id"] = self.send_widgets[i].data_id_le.text()
                data["packet"][i]["data_type"] = self.send_widgets[i].data_type_cb.currentText()
                data["packet"][i]["data_size"] = self.send_widgets[i].data_length_le.text()
                data["packet"][i]["update_ms"] = self.send_widgets[i].update_ms_le.text()
                data["packet"][i]["ip_octet_4"] = self.send_widgets[i].ip_octet_4_le.text()

                data["packet"][i]["data"] = []
                for j in range(0, int(self.send_widgets[i].data_length_le.text())):
                    data["packet"][i]["data"].append({})
                    data["packet"][i]["data"][j]["data"] = self.send_widgets[i].data_array[j].text(
                    )
                    data["packet"][i]["data"][j]["scalar"] = self.send_widgets[i].scalar_array[j].text(
                    )
                    data["packet"][i]["data"][j]["input"] = self.send_widgets[i].input_cb_array[j].currentText()

            except:
                pass
        try:
            save_file = QFileDialog.getSaveFileName(
                QFileDialog(), filter="JSON(*.json)", directory="1-Configs/")
            with open(save_file[0], 'w') as outfile:
                json.dump(data, outfile)
        except:
            pass

    def closeEvent(self, event):
        for widget in self.send_widgets:
            widget.close()


class sendWidget(QWidget):
    def __init__(self, parent=None, number=1):
        QWidget.__init__(self, parent=parent)

        super(sendWidget, self).__init__(parent)
        self.initUI(parent, number)

    def initUI(self, parent, number):
        try:
            self.xboxCont = XboxController(
                deadzone=20, scale=100, invertYAxis=True)  # controlCallBack
            self.xboxCont.start()
        except:
            pass
        self.updateTimer = QTimer()
        self.updateTimer.timeout.connect(self.sendThread)

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

        self.send = QPushButton('Send', self)
        self.send.resize(self.send.sizeHint())
        self.send.clicked.connect(self.sendEvent)

        add = QPushButton('Add', self)
        add.resize(self.send.sizeHint())
        add.clicked.connect(self.addEvent)

        remove = QPushButton('X', self)
        remove.resize(self.send.sizeHint())
        remove.clicked.connect(self.removeEvent)

        self.data_id_le = QLineEdit(self)
        self.data_length_le = QLineEdit(self)
        self.ip_octet_4_le = QLineEdit(self)

        self.data_length_le.textChanged[str].connect(self.data_length_entry)
        self.data_length = 1

        self.data_type_cb = QComboBox(self)
        for entry in data_types:
            self.data_type_cb.addItem(entry)

        self.data_array = [QLineEdit(self)]
        self.input_cb_array = [QComboBox(self)]
        self.scalar_array = [QLineEdit(self)]
        self.scalar_array[0].setText("1")

        self.update_ms_le = QLineEdit(self)
        self.update_ms_le.textChanged[str].connect(
            self.update_ms_le_textchanged)
        self.update_period_ms = 0

        self.input_cb_array[0] = self.addControls(self.input_cb_array[0])

        self.main_layout = QGridLayout(self)
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
        self.main_layout.addWidget(self.update_ms_le, 1, 9)
        self.main_layout.addWidget(self.ip_octet_4_le, 1, 10)
        self.main_layout.addWidget(self.send, 1, 11)
        self.resize(self.sizeHint())

        self.show()

    def sendEvent(self):
        data = ()
        try:
            for i in range(0, self.data_length):
                data = (data) + (int(self.data_array[i].text()),)

            packet = RoveCommPacket(int(self.data_id_le.text(
            )), data_types[self.data_type_cb.currentText()], data, self.ip_octet_4_le.text())
            RoveComm.write(packet)
            self.send.setStyleSheet('background-color: lime')
        except:
            self.send.setStyleSheet('background-color: red')
            print("Invalid Packet")

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
            if(new_length > self.data_length):
                for i in range(self.data_length, new_length):
                    self.data_array = self.data_array+[QLineEdit(self)]
                    self.main_layout.addWidget(self.data_array[i], i+1, 6)

                    self.input_cb_array = self.input_cb_array+[QComboBox(self)]
                    self.main_layout.addWidget(self.input_cb_array[i], i+1, 7)
                    self.input_cb_array[i] = self.addControls(
                        self.input_cb_array[i])

                    self.scalar_array = self.scalar_array+[QLineEdit(self)]
                    self.scalar_array[i].setText("1")
                    self.main_layout.addWidget(self.scalar_array[i], i+1, 8)

            elif(new_length < self.data_length):
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

            self.data_length = new_length

        except:
            return

    def updateXboxValues(self):
        for i in range(0, len(self.data_array)):
            text = self.input_cb_array[i].currentText()
            if(text == "Line Entry"):
                pass
            elif(text == "Left Thumb X"):
                self.data_array[i].setText(
                    str(int(float(self.scalar_array[i].text()) * self.xboxCont.LTHUMBX)))
            elif(text == "Left Thumb Y"):
                self.data_array[i].setText(
                    str(int(float(self.scalar_array[i].text()) * self.xboxCont.LTHUMBY)))
            elif(text == "Right Thumb X"):
                self.data_array[i].setText(
                    str(int(float(self.scalar_array[i].text()) * self.xboxCont.RTHUMBX)))
            elif(text == "Right Thumb Y"):
                self.data_array[i].setText(
                    str(int(float(self.scalar_array[i].text()) * self.xboxCont.RTHUMBY)))
            elif(text == "D Pad X"):
                self.data_array[i].setText(
                    str(int(float(self.scalar_array[i].text()) * self.xboxCont.DPAD[0])))
            elif(text == "D Pad Y"):
                self.data_array[i].setText(
                    str(int(float(self.scalar_array[i].text()) * self.xboxCont.DPAD[1])))
            elif(text == "L Trigger"):
                self.data_array[i].setText(
                    str(int(float(self.scalar_array[i].text()) * self.xboxCont.LTRIGGER)))
            elif(text == "R Trigger"):
                self.data_array[i].setText(
                    str(int(float(self.scalar_array[i].text()) * self.xboxCont.RTRIGGER)))
            elif(text == "L Bumper"):
                self.data_array[i].setText(
                    str(int(float(self.scalar_array[i].text()) * self.xboxCont.LB)))
            elif(text == "R Bumper"):
                self.data_array[i].setText(
                    str(int(float(self.scalar_array[i].text()) * self.xboxCont.RB)))
            elif(text == "A"):
                self.data_array[i].setText(
                    str(int(float(self.scalar_array[i].text()) * self.xboxCont.A)))
            elif(text == "B"):
                self.data_array[i].setText(
                    str(int(float(self.scalar_array[i].text()) * self.xboxCont.B)))
            elif(text == "X"):
                self.data_array[i].setText(
                    str(int(float(self.scalar_array[i].text()) * self.xboxCont.X)))
            elif(text == "Y"):
                self.data_array[i].setText(
                    str(int(float(self.scalar_array[i].text()) * self.xboxCont.Y)))
            elif(text == "Back"):
                self.data_array[i].setText(
                    str(int(float(self.scalar_array[i].text()) * self.xboxCont.BACK)))
            elif(text == "Start"):
                self.data_array[i].setText(
                    str(int(float(self.scalar_array[i].text()) * self.xboxCont.START)))
            elif(text == "L Thumb"):
                self.data_array[i].setText(
                    str(int(float(self.scalar_array[i].text()) * self.xboxCont.LEFTTHUMB)))
            elif(text == "R Thumb"):
                self.data_array[i].setText(
                    str(int(float(self.scalar_array[i].text()) * self.xboxCont.RIGHTTHUMB)))

    def update_ms_le_textchanged(self):
        try:
            self.update_period_ms = int(self.update_ms_le.text())
            if(self.update_period_ms < 100):
                self.update_period_ms = 0
                self.update_ms_le.setStyleSheet('color: red')
                self.updateTimer.stop()
            else:
                self.update_ms_le.setStyleSheet('color: black')
                self.updateTimer.start(self.update_period_ms)
        except:
            #print("Invalid time")
            self.update_period_ms = 0

    def sendThread(self):
        # print(self.update_period_ms)
        if(self.update_period_ms != 0):
            try:
                self.updateXboxValues()
            except:
                pass

            self.send.animateClick()

    def close(self):  # On close, stop threading
        print("Closing")
        try:
            self.xboxCont.stop()
        except:
            pass
        self.updateTimer.stop()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Return:
            self.sendEvent()


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
        packet = RoveCommPacket(
            ROVECOMM_SUBSCRIBE_REQUEST, 'b', (), self.subscribe_octet_4.text())
        RoveComm.write(packet)
