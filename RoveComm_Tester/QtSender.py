
import json

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QWidget, QAction, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QSplitter, QPushButton, QGridLayout, QFileDialog, QCheckBox

from RoveComm_Python import RoveCommPacket


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


# Class for window that allows a user to:
# - Send rovecomm packets to network devices
# - Save and load pre-defined packets
class Sender(QWidget):

    def __init__(self, qApp, rovecomm):
        super().__init__()

        self.rovecomm = rovecomm

        exitAct = QAction('&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(qApp.quit)

        # Add send row button and handler
        self.add_pb = QPushButton("Add Send Row")
        self.add_pb.clicked.connect(self.addEvent)

        # Load config button and handler
        self.loadJson_pb = QPushButton("Load Configs")
        self.loadJson_pb.clicked.connect(self.loadJSON)

        # Write config button and handler
        self.writeJson_pb = QPushButton("Write Config")
        self.writeJson_pb.clicked.connect(self.writeJSON)

        # Button menu layout
        self.menu_layout = QHBoxLayout()
        self.menu_layout.addWidget(self.add_pb)
        self.menu_layout.addWidget(self.loadJson_pb)
        self.menu_layout.addWidget(self.writeJson_pb)

        # Send widget array definition
        self.send_widgets = [sendWidget(self.rovecomm, self, 0)]

        # Primary layout definition
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addLayout(self.menu_layout)
        self.main_layout.addWidget(self.send_widgets[0])

        self.setWindowTitle('Sender')
        # self.setWindowIcon(QIcon(':/Rover.png'))

        self.resize(self.sizeHint())

        self.show()


    # Redraw function used after removing/adding send widgets
    def redrawWidgets(self):
        for i in range(0, len(self.send_widgets)):
            self.main_layout.removeWidget(self.send_widgets[i])
            self.main_layout.addWidget(self.send_widgets[i])
            self.send_widgets[i].setRowIndex(i)

    
    # Handler for adding a send widget
    def addEvent(self):
        self.send_widgets.append(sendWidget(
            self.rovecomm, self, len(self.send_widgets)))
        self.redrawWidgets()


    # Handler for removing a send widget
    def removeEvent(self, row_index):
        self.main_layout.removeWidget(self.send_widgets[row_index])
        self.send_widgets[row_index].close()
        self.send_widgets[row_index].deleteLater()
        self.send_widgets[row_index] = None

        self.send_widgets = self.send_widgets[:row_index] + \
            self.send_widgets[row_index + 1:]

        self.redrawWidgets()


    # Handler for loading in json files from the configs folder
    def loadJSON(self):
        try:

            # File selection
            load_files = QFileDialog.getOpenFileNames(
                QFileDialog(), filter="JSON(*.json)", directory="1-Configs/")

            print(load_files)

            # Loop through files
            for k in range(0, len(load_files[0])):
                data = json.loads(open(load_files[0][k]).read())
                start_number = len(self.send_widgets)

                print("Raw JSON: " + str(data))
                print("Number of packets: " + str(int(data["packet_count"])))

                # Loop through one file's send rows
                for i in range(0, int(data["packet_count"])):
                    try:
                        self.addEvent()
                        self.send_widgets[start_number + i].data_id_le.setText(
                            data["packet"][i]["data_id"])
                        self.send_widgets[start_number + i].update_ms_le.setText(
                            data["packet"][i]["update_ms"])
                        self.send_widgets[start_number + i].ip_octet_4_le.setText(
                            data["packet"][i]["ip_octet_4"])
                        self.send_widgets[start_number + i].data_type_cb.setCurrentText(
                            data["packet"][i]["data_type"])

                        data_size = int(data["packet"][i]["data_size"])
                        self.send_widgets[start_number + i].data_length_le.setText(
                            str(data_size))

                        # Loop through data elements
                        for j in range(0, data_size):
                            self.send_widgets[start_number + i].data_array[j].setText(
                                data["packet"][i]["data"][j]["data"])
                            self.send_widgets[start_number + i].scalar_array[j].setText(
                                data["packet"][i]["data"][j]["scalar"])
                            self.send_widgets[start_number + i].input_cb_array[j].setCurrentText(
                                data["packet"][i]["data"][j]["input"])
                    except Exception as ex:
                        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                        message = template.format(type(ex).__name__, ex.args)
                        print(message)
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)

    # Event to handle writing a json file into the configs folder

    def writeJSON(self):
        data = {
            "packet_count": len(self.send_widgets)
        }
        data["packet"] = []

        # Loop through each send row
        for i in range(0, len(self.send_widgets)):
            try:
                data["packet"].append({})
                data["packet"][i]["data_id"] = self.send_widgets[i].data_id_le.text()
                data["packet"][i]["data_type"] = self.send_widgets[i].data_type_cb.currentText()
                data["packet"][i]["data_size"] = self.send_widgets[i].data_length_le.text()
                data["packet"][i]["update_ms"] = self.send_widgets[i].update_period_ms
                data["packet"][i]["ip_octet_4"] = self.send_widgets[i].ip_octet_4_le.text()

                # Data looping per element
                data["packet"][i]["data"] = []
                for j in range(0, int(self.send_widgets[i].data_length_le.text())):
                    data["packet"][i]["data"].append({})
                    data["packet"][i]["data"][j]["data"] = self.send_widgets[i].data_array[j].text()
                    data["packet"][i]["data"][j]["scalar"] = self.send_widgets[i].scalar_array[j].text()
                    data["packet"][i]["data"][j]["input"] = self.send_widgets[i].input_cb_array[j].currentText()

            except:
                print("Unknown issue(s) with creating JSON")
                pass

        # Write the file
        try:
            save_file = QFileDialog.getSaveFileName(
                QFileDialog(), filter="JSON(*.json)", directory="1-Configs/")
            with open(save_file[0], 'w') as outfile:
                json.dump(data, outfile)
        except:
            print("Unknown issue with writing & saving JSON")


    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()


    def closeEvent(self, event):
        for widget in self.send_widgets:
            widget.close()


# Class defines a send row for the sender widget
class sendWidget(QWidget):
    def __init__(self, rovecomm, parent=None, row_index=1):
        QWidget.__init__(self, parent=parent)

        super(sendWidget, self).__init__(parent)
        self.rovecomm = rovecomm

        # Defining xbox controller
        try:
            self.xboxCont = XboxController(
                deadzone=20, scale=100, invertYAxis=True)  # controlCallBack
            self.xboxCont.start()
        except:
            pass

        self.updateTimer = QTimer()
        self.updateTimer.timeout.connect(self.sendThread)

        self.row_index = row_index

        # Send button and handler assignment
        self.send = QPushButton('Send', self)
        self.send.resize(self.send.sizeHint())
        self.send.clicked.connect(self.sendEvent)

        # Remove button and handler assignment
        remove = QPushButton('X', self)
        remove.resize(self.send.sizeHint())
        remove.clicked.connect(self.removeEvent)

        # Send enable checkbox
        self.send_check = QCheckBox("Enable")
        self.send_check.stateChanged.connect(self.enabled)

        # Inputs for dataID and IP Octet
        self.data_id_le = QLineEdit(self)
        self.data_id_le.textChanged[str].connect(self.update_le_is_number)
        self.ip_octet_4_le = QLineEdit(self)
        self.ip_octet_4_le.textChanged[str].connect(self.update_octet_le)

        # Arrays of qtWidgets for data pieces of a packet
        self.data_array = []
        self.input_cb_array = []
        self.scalar_array = []

        # Data size input definition and handler
        self.data_length_le = QLineEdit(self)
        self.data_length_le.textChanged[str].connect(self.update_le_is_number)
        self.data_length_le.textChanged[str].connect(self.data_length_entry)
        self.data_length = 0

        # Data type input, populated from list
        self.data_type_cb = QComboBox(self)
        for entry in data_types:
            self.data_type_cb.addItem(entry)

        # Packet rate input
        self.update_ms_le = QLineEdit(self)
        self.update_ms_le.textChanged[str].connect(
            self.update_ms_le_textchanged)
        self.update_period_ms = 0

        # Layout definition and assignments
        self.main_layout = QGridLayout(self)

        # Row for name headers
        self.main_layout.addWidget(QLabel('IP Octet 4', self), 0, 1)
        self.main_layout.addWidget(QLabel('Data ID', self), 0, 2)
        self.main_layout.addWidget(QLabel('Data Size', self), 0, 4)
        self.main_layout.addWidget(QLabel('Data', self), 0, 5)
        self.main_layout.addWidget(QLabel('Input', self), 0, 6)
        self.main_layout.addWidget(QLabel('Scalar', self), 0, 7)
        self.main_layout.addWidget(QLabel('Send Rate (ms)', self), 0, 8)

        self.main_layout.addWidget(remove, 1, 0)
        self.main_layout.addWidget(self.ip_octet_4_le, 1, 1)
        self.main_layout.addWidget(self.data_id_le, 1, 2)
        self.main_layout.addWidget(self.data_type_cb, 1, 3)
        self.main_layout.addWidget(self.data_length_le, 1, 4)
        # Columns 5, 6 & 7 for dynamic data fields
        self.main_layout.addWidget(self.update_ms_le, 1, 8)
        self.main_layout.addWidget(self.send_check, 1, 9)
        self.main_layout.addWidget(self.send, 1, 10)

        self.resize(self.sizeHint())

        self.show()

        # Use the callbacks to populate the data section and enable state
        self.data_length_le.setText("1")
        self.send_check.setChecked(True)
        self.send_check.setChecked(False)


    # Handler for sending packets
    def sendEvent(self):
        data = ()
        try:
            for i in range(0, self.data_length):
                data = (data) + (int(self.data_array[i].text()),)

            packet = RoveCommPacket(int(self.data_id_le.text(
            )), data_types[self.data_type_cb.currentText()], data, self.ip_octet_4_le.text())
            self.rovecomm.write(packet)
            self.update_text_color(True, self.send)
        except:
            self.update_text_color(False, self.send)
            print("Invalid Packet")


    # Handler for removing a sender widget row
    def removeEvent(self, parent):
        self.parent().removeEvent(self.row_index)


    # Sets the row index for the sender widget, used in parent
    def setRowIndex(self, row_index):
        self.row_index = row_index


    # Handler for data size input. 
    # Dynamically generates data array qt elements accordingly
    def data_length_entry(self):
        try:

            # Attempt int-ifying the text for a size
            new_length = int(self.data_length_le.text())

            # Add elements as necessary
            if(new_length > self.data_length):
                for i in range(self.data_length, new_length):
                    self.data_array = self.data_array+[QLineEdit(self)]
                    self.main_layout.addWidget(self.data_array[i], i+1, 5)

                    self.input_cb_array = self.input_cb_array+[QComboBox(self)]
                    self.main_layout.addWidget(self.input_cb_array[i], i+1, 6)
                    for k in controls:
                        self.input_cb_array[i].addItem(k)

                    self.scalar_array = self.scalar_array+[QLineEdit(self)]
                    self.scalar_array[i].textChanged[str].connect(self.update_le_is_float)
                    self.scalar_array[i].setText("1")
                    self.main_layout.addWidget(self.scalar_array[i], i+1, 7)

            # Remove elements as necessary
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


    # Xbox values updater
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


    # Handler for rate input
    def update_ms_le_textchanged(self):
        try:
            self.update_period_ms = int(self.update_ms_le.text())
            if(self.update_period_ms < 100):
                self.update_period_ms = 0
                self.update_text_color(False, self.update_ms_le)
                self.updateTimer.stop()
            else:
                self.update_text_color(True, self.update_ms_le)
                self.updateTimer.start(self.update_period_ms)
        except:
            self.update_period_ms = 0
            self.update_text_color(False, self.update_ms_le)

    
    # Updates line edit color according to if it contains a number
    def update_le_is_number(self):
        try:
            int(self.sender().text())
            self.update_text_color(True, self.sender())
        except:
            self.update_text_color(False, self.sender())  


    # Updates line edit color according to if it contains a float
    def update_le_is_float(self):
        try:
            float(self.sender().text())
            self.update_text_color(True, self.sender())
        except:
            self.update_text_color(False, self.sender())  


    # Handler for octet, filter for valid input
    def update_octet_le(self):
        try:
            if int(self.sender().text()) < 256:
                self.update_text_color(True, self.sender())
            else:
                self.update_text_color(False, self.sender())
        except:
            self.update_text_color(False, self.sender())


    # Updates text color on line edits to notify of bad input
    def update_text_color(self, status, element):
        if status:
            element.setStyleSheet('')
        else:
            element.setStyleSheet('color:red')


    # Thread method executed when the update period is valid
    def sendThread(self):
        if(self.update_period_ms != 0):
            try:
                self.updateXboxValues()
            except:
                pass

            self.send.animateClick()


    # Handler for enable checkbox, sets state of send button
    def enabled(self, enabled):
        self.send.setEnabled(enabled)


    def close(self):
        try:
            self.xboxCont.stop()
        except:
            pass
        self.updateTimer.stop()


    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Return:
            self.sendEvent()
