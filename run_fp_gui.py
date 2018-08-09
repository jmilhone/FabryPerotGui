from __future__ import division, print_function
from PyQt5 import QtCore, QtGui, QtWidgets
from source.views.main_window import MainWindow
from source.controller.main_controller import MainController
from source.models.model import FabryPerotModel
import sys
import argparse
import os.path as path


class App(QtWidgets.QApplication):
    """

    """
    def __init__(self, sys_argv, filename=None, bg_filename=None):
        super(App, self).__init__(sys_argv)
        self.model = FabryPerotModel()
        self.controller = MainController(self.model)
        self.view = MainWindow(self.model, self.controller, filename=filename, bg_filename=bg_filename)
        self.view.setGeometry(100, 100, 2000, 1000)
        self.view.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fabry-Perot Gui for Image Processing")
    parser.add_argument("--image", "-I", type=str, help="file path to image", default=None)
    parser.add_argument("--background", "-B", type=str, help="file path to background image", default=None)
    args = parser.parse_args()

    filename = None
    bg_filename = None

    if args.image is not None:
        filename = path.expanduser(args.image)
        filename = path.abspath(filename)

    if bg_filename is not None:
        bg_filename = path.expanduser(args.background)
        bg_filename = path.abspath(bg_filename)

    app = App(sys.argv, filename=filename, bg_filename=bg_filename)
    sys.exit(app.exec_())
