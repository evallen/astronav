# This Python file uses the following encoding: utf-8
import sys, subprocess
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QTextEdit
from PySide6.QtGui import QPixmap

class PhotoViewer(QWidget):
    def __init__(self):
        super().__init__()

        # Set window title
        self.setWindowTitle("ASTRONAV")

        # Create image labels
        self.image_label_1 = QLabel(self)
        self.image_label_2 = QLabel(self)
        self.image_label_3 = QLabel(self)
        self.image_label_4 = QLabel(self)

        # Load images
        self.image_1 = QPixmap("images/image1.jpg")
        self.image_2 = QPixmap("images/image2.jpg")
        self.image_3 = QPixmap("images/image3.jpg")
        self.image_4 = QPixmap("images/image4.jpg")

        # Set images to labels
        self.image_label_1.setPixmap(self.image_1)
        self.image_label_2.setPixmap(self.image_2)
        self.image_label_3.setPixmap(self.image_3)
        self.image_label_4.setPixmap(self.image_4)

        # Create grid layout
        layout = QGridLayout()
        layout.addWidget(self.image_label_1, 0, 0)
        layout.addWidget(self.image_label_2, 0, 1)
        layout.addWidget(self.image_label_3, 1, 0)
        layout.addWidget(self.image_label_4, 1, 1)

        # Create text edit
        self.text_edit = QTextEdit(self)

        # Add text edit to layout
        layout.addWidget(self.text_edit, 2, 0, 1, 2)

        # Set layout
        self.setLayout(layout)

        # Read data from stdin and display it in the text edit
        #self.show()
#        while True:
#            data = sys.stdin.readline().rstrip()
#            if not data:
#                break
#            self.text_edit.append(data)

def showGUI():
    app = QApplication(sys.argv)
    photo_viewer = PhotoViewer()
    photo_viewer.show()
    app.exec()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    photo_viewer = PhotoViewer()
    photo_viewer.show()
    sys.exit(app.exec())
