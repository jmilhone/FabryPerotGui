from __future__ import division, print_function
from PyQt5 import QtCore, QtGui, QtWidgets
from source.views.main_window import MainWindow
import sys


class App(QtWidgets.QApplication):
    def __init__(self, sys_argv):
        super(App, self).__init__(sys_argv)
        self.model = None  # DataModel()
        self.controller = None  # MainController(self.model)
        self.view = MainWindow(self.model, self.controller)
        self.view.show()


if __name__ == "__main__":
    app = App(sys.argv)
    sys.exit(app.exec_())
