from __future__ import print_function, absolute_import, division
from PyQt5 import QtGui, QtWidgets, QtCore
from .matplotlib_widget import MatplotlibWidget
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable


class MainWindow(QtWidgets.QMainWindow):
    """

    :param model: data model
    :type model: source.models.model.FabryPerotModel
    :param controller: controller
    :type controller: source.controller.main_controller.MainController
    :param plot_window: matplotlib window with navigation toolbar
    :type plot_window: source.views.matplotlib_widget.MatplotlibWidget
    """

    def __init__(self, model, controller):
        super(MainWindow, self).__init__()
        self.model = model
        self.controller = controller

        self.plot_window = MatplotlibWidget()
        self.central_widget = QtWidgets.QWidget()
        self.hbox = QtWidgets.QHBoxLayout()

        self.sidebar_vbox = QtWidgets.QVBoxLayout()
        self.x0_guess_box = QtWidgets.QHBoxLayout()
        self.y0_guess_box = QtWidgets.QHBoxLayout()

        self.x0_label = QtWidgets.QLabel()
        self.y0_label = QtWidgets.QLabel()

        self.x0_entry = QtWidgets.QDoubleSpinBox()
        self.y0_entry = QtWidgets.QDoubleSpinBox()
        self.init_UI()

        self.model.subscribe_update_func(self.display_image_data, registry='image_data')
        image_name = "C:/Users/jason/Argon_calib.nef"
        bg_name = "C:/Users/jason/Argon_calib_bg.nef"
        print('calling read image')
        self.controller.read_image_data(image_name, bg_name)

    def init_UI(self):
        self.x0_label.setText("X Center Guess: ")
        self.y0_label.setText("Y Center Guess: ")

        self.x0_entry.setRange(0.0, 100000.0)
        self.y0_entry.setRange(0.0, 100000.0)

        self.x0_entry.setValue(0.0)
        self.y0_entry.setValue(0.0)

        self.x0_guess_box.addWidget(self.x0_label)
        self.x0_guess_box.addWidget(self.x0_entry)

        self.y0_guess_box.addWidget(self.y0_label)
        self.y0_guess_box.addWidget(self.y0_entry)

        self.sidebar_vbox.addLayout(self.x0_guess_box)
        self.sidebar_vbox.addLayout(self.y0_guess_box)
        self.sidebar_vbox.addStretch()

        self.hbox.addWidget(self.plot_window, 10)
        self.hbox.addLayout(self.sidebar_vbox)
        self.central_widget.setLayout(self.hbox)
        self.setCentralWidget(self.central_widget)

    def display_image_data(self):
        image_data = self.model.image

        ax = self.plot_window.axs
        canvas = self.plot_window.canvas
        fig = self.plot_window.figure
        toolbar = self.plot_window.toolbar

        divider = make_axes_locatable(ax)
        cax = divider.append_axes('right', size='5%', pad=0.05)
        im = ax.imshow(image_data)
        fig.colorbar(im, cax=cax)

        if self.model.center is not None:
            x0, y0 = self.model.center
            ax.axvline(x0, color='C3')
            ax.axhline(y0, color='C1')

        toolbar.update()
        toolbar.push_current()
        canvas.draw()


