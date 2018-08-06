from __future__ import print_function, absolute_import, division
from PyQt5 import QtGui, QtWidgets, QtCore
from .matplotlib_widget import MatplotlibWidget

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, model, controller):
        super(MainWindow, self).__init__()
        self.model = model
        self.controller = controller

        self.plot_window = MatplotlibWidget()
        self.central_widget = QtWidgets.QWidget()
        self.vbox = QtWidgets.QVBoxLayout()
        self.init_UI()

    def init_UI(self):

        self.vbox.addWidget(self.plot_window)
        self.central_widget.setLayout(self.vbox)
        self.setCentralWidget(self.central_widget)
        #self.show()
