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
    :attribute plot_window: matplotlib window with navigation toolbar
    :type plot_window: source.views.matplotlib_widget.MatplotlibWidget
    """

    def __init__(self, model, controller):
        super(MainWindow, self).__init__()
        self.model = model
        self.controller = controller
        self.cb = None

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

        self.find_center_button = QtWidgets.QPushButton()

        self.center_label = QtWidgets.QLabel()

        self.get_ringsum_button = QtWidgets.QPushButton()
        # Put all gui elements before this line!
        self.init_UI()

        # image_name = "C:/Users/jason/Argon_calib.nef"
        # bg_name = "C:/Users/jason/Argon_calib_bg.nef"

        image_name = "/Users/milhone/Argon_calib.nef"
        bg_name = "/Users/milhone/Argon_calib_bg.nef"

        print('calling read image')
        self.controller.read_image_data(image_name, bg_name)

        # Subscribe functions for updates in model
        self.model.subscribe_update_func(self.display_image_data, registry='image_data')
        self.model.subscribe_update_func(self.update_initial_center_entry, registry='image_data')
        self.model.subscribe_update_func(self.plot_ringsum, registry='ringsum_data')
        self.model.subscribe_update_func(self.update_center_label, registry='image_data')

        # Set up PyQt signals for GUI Events
        self.find_center_button.clicked.connect(self.find_center)
        self.get_ringsum_button.clicked.connect(self.find_ringsum)


    def init_UI(self):
        self.x0_label.setText("X Center Guess: ")
        self.y0_label.setText("Y Center Guess: ")

        self.x0_entry.setRange(0.0, 100000.0)
        self.y0_entry.setRange(0.0, 100000.0)

        self.x0_entry.setValue(0.0)
        self.y0_entry.setValue(0.0)

        self.find_center_button.setText("Find Center")
        self.center_label.setText("Center: ")

        self.get_ringsum_button.setText("Find Ringsum")
        self.get_ringsum_button.setDisabled(True)

        self.x0_guess_box.addWidget(self.x0_label)
        self.x0_guess_box.addWidget(self.x0_entry)

        self.y0_guess_box.addWidget(self.y0_label)
        self.y0_guess_box.addWidget(self.y0_entry)

        self.sidebar_vbox.addLayout(self.x0_guess_box)
        self.sidebar_vbox.addLayout(self.y0_guess_box)
        self.sidebar_vbox.addWidget(self.find_center_button)
        self.sidebar_vbox.addWidget(self.center_label)
        self.sidebar_vbox.addWidget(self.get_ringsum_button)
        self.sidebar_vbox.addStretch()

        self.hbox.addWidget(self.plot_window, 10)
        self.hbox.addLayout(self.sidebar_vbox, 4)
        self.central_widget.setLayout(self.hbox)
        self.setCentralWidget(self.central_widget)

    def display_image_data(self):

        self.plot_window.axs.cla()

        if self.cb is not None:
            self.cb.remove()

        image_data = self.model.image
        im = self.plot_window.axs.imshow(image_data)
        self.cb = self.plot_window.figure.colorbar(im, ax=self.plot_window.axs,
                                         fraction=0.03, pad=0.04)

        if self.model.center is not None:
            x0, y0 = self.model.center
            self.plot_window.axs.axvline(x0, color='C3')
            self.plot_window.axs.axhline(y0, color='C1')
        self.plot_window.axs.axis('image')

        self.plot_window.figure.tight_layout()
        self.plot_window.toolbar.update()
        self.plot_window.toolbar.push_current()
        self.plot_window.canvas.draw()

    def update_initial_center_entry(self):
        ny, nx = self.model.image.shape

        if self.x0_entry.value() == 0.0:
            self.x0_entry.setValue(nx/2.0)
        if self.y0_entry.value() == 0.0:
            self.y0_entry.setValue(ny/2.0)

    def update_center_label(self):
        if self.model.center is None:
            return

        x0, y0 = self.model.center

        output_string = "Center: ({0:.2f},{1:.2f})".format(x0, y0)
        self.center_label.setText(output_string)
        self.get_ringsum_button.setEnabled(True)

    def find_center(self, pushed):
        xguess = self.x0_entry.value()
        yguess = self.y0_entry.value()

        self.controller.find_center(xguess, yguess)

    def find_ringsum(self, pushed):
        self.controller.get_ringsum()

    def plot_ringsum(self):
        r = self.model.r
        sig = self.model.ringsum
        sig_sd = self.model.ringsum_err

        self.plot_window.axs.cla()

        if self.cb is not None:
            self.cb.remove()

        self.plot_window.axs.errorbar(r, sig, yerr=sig_sd, color='C0')
        self.plot_window.axs.set_xlabel("R (px)")
        self.plot_window.axs.set_ylabel("Counts")
        self.plot_window.axs.axis('tight')

        self.plot_window.figure.tight_layout()
        self.plot_window.toolbar.update()
        self.plot_window.toolbar.push_current()
        self.plot_window.canvas.draw()
