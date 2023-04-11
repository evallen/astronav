# This Python file uses the following encoding: utf-8
import sys, subprocess
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QTextEdit, QMainWindow, QLineEdit, QPushButton, QTableView, QTableView, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtGui import QPixmap, QTextCursor
from PySide6.QtCore import QObject, QEvent, QCoreApplication, QThread, Qt, QAbstractTableModel, QSize #, QVariant
from main import astronav

class UI(QWidget):
    buttons_on = True
    av = astronav()

    def __init__(self):
        super().__init__()

        # Set window title
        self.setWindowTitle("ASTRONAV")

        # Create image labels
        self.image_label_1 = QLabel(self)

        # Load images
        self.image_1 = QPixmap("images/image1.jpg")

        # Set images to labels
        self.image_label_1.setPixmap(self.image_1)

        # Create grid layout
        layout = QGridLayout()
        layout.addWidget(self.image_label_1, 0, 0, 4, 4)

        #QLineEdit
        self.control = QLineEdit(self)
        self.control.setReadOnly(True)
        self.control.setText("LAT, LONG")
        layout.addWidget(self.control, 4, 0, 1, 4)

        #QLineEdit
        self.control = QLineEdit(self)
        self.control.setReadOnly(True)
        self.control.setText("ALTITUDE")
        layout.addWidget(self.control, 5, 0)

        self.takebutton = QPushButton('TAKE')
        layout.addWidget(self.takebutton, 5, 1)
        self.takebutton.clicked.connect(self.take)

        self.evalbutton = QPushButton('EVAL')
        layout.addWidget(self.evalbutton, 5, 2)
        self.evalbutton.clicked.connect(self.eval)

        self.resetbutton = QPushButton('RESET')
        layout.addWidget(self.resetbutton, 5, 3)
        self.resetbutton.clicked.connect(self.reset)

        #QTextEdit - Raw console output
        self.rawconsole = QTextEdit(self)
        self.rawconsole.setText("WELCOME TO ASTRONAV\nastronav> ")
        layout.addWidget(self.rawconsole, 6, 0, 1, 4) # Add text edit to layout
        
        # tableLabel = QLabel("Run Status")
        # layout.addWidget(tableLabel, 0, 4, 1, 1) # Add text edit to layout

        # Create the QTableView and set the model
        self.table_view = QTableView()

        self.model = SpreadsheetModel([['OK', '12.3', '0'], ['OK', '32.9', '0'], ['OK', '56.7', '0']])
        self.table_view.setModel(self.model)
        
        # Add the QTableView to the layout
        layout.addWidget(self.table_view, 0, 4, 7, 4) # Add text edit to layout


        # Set layout
        self.setLayout(layout)

        # Read data from stdin and display it in the text edit
        #self.show()
#        while True:
#            data = sys.stdin.readline().rstrip()
#            if not data:
#                break
#            self.text_edit.append(data)

        # print line to console
    def out_line(self, string):
        self.rawconsole.moveCursor (QTextCursor.End);
        self.rawconsole.insertPlainText(string);

        # disable buttons during processing
    def toggle_buttons(self):
        self.buttons_on = not self.buttons_on
        self.takebutton.setEnabled(self.buttons_on)
        self.evalbutton.setEnabled(self.buttons_on)
        self.resetbutton.setEnabled(self.buttons_on)

    def take(self):
        # for now does awkward with stuff not plugged in
        #if self.av.takeFunct():
        #    self.out_line("Success!\n")
        #else:
        #    self.out_line("Failure\n")
        self.toggle_buttons()
        return 0

    def eval(self):
        self.toggle_buttons()
        return 0

    def reset(self):
        self.toggle_buttons()
        return 0


class Window(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.gui = UI()
        self.setCentralWidget(self.gui)
    
    def closeWindow():
        pass


# gui component holder which will be moved to main thread
class gui_launcher(QThread):
    def __init__(self):
        super().__init__()
        self.w = UI()
        self.w.moveToThread(self)
        self.w.show()


# https://stackoverflow.com/questions/73260198/how-to-interact-with-pyqt5-main-thread-from-another-thread-in-another-file
def showGUI():
    app = QApplication(sys.argv)
    gl = Window()
    gl.show()
    app.exec()



class SpreadsheetModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
        self._header_labels = ['Status', 'RA', 'DEC']
        self._column_widths = [100, 150, 200]
        
    def rowCount(self, parent=None):
        return len(self._data)
    
    def columnCount(self, parent=None):
        return len(self._header_labels)
    
    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]
        return None #QVariant()
    
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._header_labels[section]
            elif orientation == Qt.Vertical:
                return str(section + 1)
        # elif role == Qt.SizeHintRole:  # Set column width
        #     if orientation == Qt.Horizontal:
        #         return QSize(self._column_widths[section], 0)
        return None #QVariant()

    def insertRows(self, row, count, parent=None):
        self.beginInsertRows(parent, row, row + count - 1)
        self._data.append([''] * self.columnCount())
        self.endInsertRows()
        return True

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        return False

# class Spreadsheet(QWidget):
    
#     def __init__(self):
#         super().__init__()
#         self.initUI()
        
#     def initUI(self):
#         pass
    
    # def add_data(self):
    #     # Get the new data from the form
    #     name = self.name_edit.text()
    #     age = self.age_edit.text()
    #     gender = self.gender_edit.text()
        
    #     # Update the model with the new data
    #     row = self.model.rowCount()
    #     self.model.insertRows(row, 1)
    #     self.model.setData(self.model.index(row, 0), name, Qt.EditRole)
    #     self.model.setData(self.model.index(row, 1), age, Qt.EditRole)
    #     self.model.setData(self.model.index(row, 2), gender, Qt.EditRole)

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     ex = Spreadsheet()
#     sys.exit(app.exec_())

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     photo_viewer = PhotoViewer()
#     photo_viewer.show()
#     sys.exit(app.exec())

if __name__ == '__main__':
    showGUI()
