from __future__ import print_function, absolute_import, division
from PyQt5 import QtGui, QtWidgets, QtCore
from .matplotlib_widget import MatplotlibWidget
# import matplotlib.pyplot as plt
# from mpl_toolkits.axes_grid1 import make_axes_locatable


class MainWindow(QtWidgets.QMainWindow):
    """

    :param model: data model
    :type model: source.models.model.FabryPerotModel
    :param controller: controller
    :type controller: source.controller.main_controller.MainController
    :attribute plot_window: matplotlib window with navigation toolbar
    :type image_plot_window: source.views.matplotlib_widget.MatplotlibWidget
    """

    def __init__(self, model, controller, filename=None, bg_filename=None):
        print(bg_filename)
        super(MainWindow, self).__init__()
        self.model = model
        self.controller = controller
        self.cb = None
        # self.setStyleSheet("background-color: #5f6063;")
        # self.setStyleSheet("background-color: #c1c1c1")
        #self.setStyleSheet("background-color: #ffffff;")
        # set up menu bar and qactions
        # self.menu = QtWidgets.QMenuBar()
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu('File')

        self.open_image_action = QtWidgets.QAction('Open Images...', self)
        self.save_ringsum_action = QtWidgets.QAction('Save Ringsum Data...', self)

        self.tabs = QtWidgets.QTabWidget()
        # self.image_tab = self.ta
        #self.options_frame = QtWidgets.QFrame()
        #self.options_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        #self.options_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        #self.options_frame.setLineWidth(2)
        # self.options_frame.setStyleSheet("border: 1px solid rgb(0, 255, 0);")
        #self.options_frame.setFrameStyle('border: 1px solid rgb (0, 255, 0);')
        # self.options_frame.setStyleSheet("background-color: #949699;")
        #self.options_frame.setStyleSheet("background-color: #ffffff")

        self.image_plot_window = MatplotlibWidget(self)
        self.ringsum_plot_window = MatplotlibWidget(self)
        print(self.image_plot_window.figure, self.ringsum_plot_window.figure)
        self.central_widget = QtWidgets.QWidget()
        self.hbox = QtWidgets.QHBoxLayout()

        self.sidebar_vbox = QtWidgets.QVBoxLayout()
        #self.sidebar_vbox = QtWidgets.QVBoxLayout(self.options_frame)
        self.x0_guess_box = QtWidgets.QHBoxLayout()
        self.y0_guess_box = QtWidgets.QHBoxLayout()

        self.x0_label = QtWidgets.QLabel()
        self.y0_label = QtWidgets.QLabel()

        self.x0_entry = QtWidgets.QDoubleSpinBox()
        self.y0_entry = QtWidgets.QDoubleSpinBox()

        self.binsize_label = QtWidgets.QLabel()
        self.binsize_entry = QtWidgets.QDoubleSpinBox()
        self.binsize_box = QtWidgets.QHBoxLayout()

        self.npix_label = QtWidgets.QLabel()
        self.npix_entry = QtWidgets.QSpinBox()
        self.npix_box = QtWidgets.QHBoxLayout()

        self.display_image_button = QtWidgets.QPushButton()
        self.find_center_button = QtWidgets.QPushButton()

        self.button_box = QtWidgets.QHBoxLayout()

        self.center_label = QtWidgets.QLabel()

        self.get_ringsum_button = QtWidgets.QPushButton()

        self.status_label = QtWidgets.QLabel()

        self.options_group = QtWidgets.QGroupBox("Options")
        self.options_group.setObjectName('OptionsGroup')
        # Put all gui elements before this line!
        #self.options_group.setStyleSheet("QGroupBox#OptionsGroup {border: 1px solid gray; border-radius: 3px;}; QGroupBox::title {subcontrol-origin: margin; left: 3px; padding: 3 0 3 0;}")
        self.options_group.setStyleSheet("QGroupBox::title {subcontrol-origin: margin; left: 3px; bottom: 5 px; padding: 3 0 3 0;} QGroupBox#OptionsGroup {border: 1px solid gray; border-radius: 3px; font-weight: bold}")
        self.setStyleSheet("padding: 2 0 2 0;")
        self.init_UI()

        # Subscribe functions for updates in model
        self.model.subscribe_update_func(self.display_image_data, registry='image_data')
        self.model.subscribe_update_func(self.update_initial_center_entry, registry='image_data')
        self.model.subscribe_update_func(self.plot_ringsum, registry='ringsum_data')
        self.model.subscribe_update_func(self.update_center_label, registry='image_data')
        self.model.subscribe_update_func(self.update_status_label, registry='status')
        self.model.subscribe_update_func(self.enable_save_ringsum, registry='ringsum_data')

        # Set up PyQt signals for GUI Events
        self.find_center_button.clicked.connect(self.find_center)
        self.get_ringsum_button.clicked.connect(self.find_ringsum)
        self.open_image_action.triggered.connect(self.open_images_dialog)
        self.display_image_button.clicked.connect(self.display_image_button_pressed)

        print('im here...')
        print(filename, bg_filename)
        if filename and bg_filename:
            print('why im not here')
            self.controller.read_image_data(filename, bg_filename, npix=self.npix_entry.value())

    def init_UI(self):
        """

        :return:
        """
        # options for qactions
        self.open_image_action.setCheckable(False)
        self.save_ringsum_action.setCheckable(False)
        self.save_ringsum_action.setEnabled(False)

        # add actions to menu bar
        self.file_menu.addAction(self.open_image_action)
        self.file_menu.addAction(self.save_ringsum_action)

        self.x0_label.setText("X Center Guess: ")
        self.y0_label.setText("Y Center Guess: ")

        self.npix_label.setText("Super Pixel Size")
        self.npix_entry.setRange(1, 10)
        self.npix_entry.setValue(5)
        #self.npix_label.setFrameShape(QtWidgets.QFrame.Panel)
        #self.npix_label.setFrameShadow(QtWidgets.QFrame.Sunken)
        #self.npix_label.setLineWidth(2)

        self.binsize_label.setText("Binsize (px)")
        self.binsize_entry.setRange(0.01, 1)
        self.binsize_entry.setValue(0.1)

        self.x0_entry.setRange(0.0, 100000.0)
        self.y0_entry.setRange(0.0, 100000.0)

        self.x0_entry.setValue(0.0)
        self.y0_entry.setValue(0.0)

        self.display_image_button.setText("Display Image")

        self.find_center_button.setText("Find Center")
        self.center_label.setText("Center: ")

        self.get_ringsum_button.setText("Find Ringsum")
        self.get_ringsum_button.setDisabled(True)

        self.status_label.setText("Status: IDLE")

        self.binsize_box.addWidget(self.binsize_label)
        self.binsize_box.addWidget(self.binsize_entry)

        self.npix_box.addWidget(self.npix_label)
        self.npix_box.addWidget(self.npix_entry)

        self.x0_guess_box.addWidget(self.x0_label)
        self.x0_guess_box.addWidget(self.x0_entry)

        self.y0_guess_box.addWidget(self.y0_label)
        self.y0_guess_box.addWidget(self.y0_entry)

        self.button_box.addWidget(self.display_image_button)
        self.button_box.addWidget(self.find_center_button)
        self.button_box.addWidget(self.get_ringsum_button)

        self.sidebar_vbox.addLayout(self.npix_box)
        self.sidebar_vbox.addLayout(self.x0_guess_box)
        self.sidebar_vbox.addLayout(self.y0_guess_box)
        self.sidebar_vbox.addWidget(self.center_label)
        self.sidebar_vbox.addLayout(self.binsize_box)
        self.sidebar_vbox.addLayout(self.button_box)
        self.sidebar_vbox.addStretch()
        self.sidebar_vbox.addWidget(self.status_label)

        # self.hbox.addWidget(self.plot_window, 10)
        self.tabs.addTab(self.image_plot_window, "Image")
        self.tabs.addTab(self.ringsum_plot_window, "Ring Sum")
        self.hbox.addWidget(self.tabs, 10)
        self.options_group.setLayout(self.sidebar_vbox)
        self.hbox.addWidget(self.options_group, 4)
        #self.hbox.addLayout(self.sidebar_vbox, 4)
        #self.hbox.addWidget(self.options_frame)
        self.central_widget.setLayout(self.hbox)
        self.setCentralWidget(self.central_widget)

    def display_image_data(self):
        """

        :return:
        """

        self.image_plot_window.axs.cla()

        if self.cb is not None:
            self.cb.remove()
            self.cb = None

        image_data = self.model.image
        im = self.image_plot_window.axs.imshow(image_data)
        self.cb = self.image_plot_window.figure.colorbar(im, ax=self.image_plot_window.axs,
                                                         fraction=0.03, pad=0.04)

        if self.model.center is not None:
            x0, y0 = self.model.center
            self.image_plot_window.axs.axvline(x0, color='C3')
            self.image_plot_window.axs.axhline(y0, color='C1')
        self.image_plot_window.axs.axis('image')

        self.image_plot_window.figure.tight_layout()
        self.image_plot_window.toolbar.update()
        self.image_plot_window.toolbar.push_current()
        self.image_plot_window.canvas.draw()
        self.tabs.setCurrentIndex(0)

    def update_initial_center_entry(self):
        """

        :return:
        """
        ny, nx = self.model.image.shape

        if self.x0_entry.value() == 0.0:
            self.x0_entry.setValue(nx/2.0)
            # self.x0_entry.setValue(2985.7)
        if self.y0_entry.value() == 0.0:
            self.y0_entry.setValue(ny/2.0)
            # self.y0_entry.setValue(1934.0)

    def update_center_label(self):
        """

        :return:
        """
        if self.model.center is None:
            return

        x0, y0 = self.model.center

        output_string = "Center: ({0:.2f},{1:.2f})".format(x0, y0)
        self.center_label.setText(output_string)
        self.get_ringsum_button.setEnabled(True)

    def find_center(self, pushed):
        """

        :param pushed:
        :return:
        """
        xguess = self.x0_entry.value()
        yguess = self.y0_entry.value()

        self.controller.find_center(xguess, yguess)

    def find_ringsum(self, pushed):
        """

        :param pushed:
        :return:
        """
        self.controller.get_ringsum(binsize=self.binsize_entry.value())

    def plot_ringsum(self):
        """

        :return:
        """
        r = self.model.r
        sig = self.model.ringsum
        sig_sd = self.model.ringsum_err

        self.ringsum_plot_window.axs.cla()

        # if self.cb is not None:
        #     self.cb.remove()
        #     self.cb = None

        self.ringsum_plot_window.axs.errorbar(r, sig, yerr=sig_sd, color='C0')
        self.ringsum_plot_window.axs.set_xlabel("R (px)")
        self.ringsum_plot_window.axs.set_ylabel("Counts")
        self.ringsum_plot_window.axs.axis('tight')

        self.ringsum_plot_window.figure.tight_layout()
        self.ringsum_plot_window.toolbar.update()
        self.ringsum_plot_window.toolbar.push_current()
        self.ringsum_plot_window.canvas.draw()
        self.tabs.setCurrentIndex(1)

    def open_images_dialog(self, checked):
        """

        :param checked:
        :return:
        """
        dlg = QtWidgets.QFileDialog(self, 'Pick an Image')
        dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dlg.setNameFilters(["Images (*.nef)", "Numpy (*.npy)", "HDF5 (*.h5)"])
        dlg.selectNameFilter("Images (*.nef)")

        if not dlg.exec_():
            return

        filename = dlg.selectedFiles()[0]

        dlg = QtWidgets.QFileDialog(self, 'Pick a Background Image')
        dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dlg.setNameFilters(["Images (*.nef)", "Numpy (*.npy)", "HDF5 (*.h5)"])
        dlg.selectNameFilter("Images (*.nef)")

        if not dlg.exec_():
            return

        bg_filename = dlg.selectedFiles()[0]
        npix = self.npix_entry.value()
        self.controller.read_image_data(filename, bg_filename, npix=npix)

    def display_image_button_pressed(self, checked):
        fname = self.model.image_name
        bg_fname = self.model.background_name
        npix = self.model.super_pixel
        data = self.model.image
        user_npix = self.npix_entry.value()

        if fname and bg_fname:
            # we have file names
            if data is None or user_npix != npix:
                # we either don't have image data or we need to reopen for super pixelate
                self.controller.read_image_data(fname, bg_fname, npix=user_npix)
            else:
                # shortcut to having image data updates
                self.model.announce_update(registry='image_data')
        else:
            # Need to retrieve filenames from the user
            self.open_images_dialog(None)

    def update_status_label(self):
        """

        :return:
        """
        new_status = self.model.status
        status_str = "Status: {0:s}".format(new_status)
        self.status_label.setText(status_str)

    def enable_save_ringsum(self):
        self.save_ringsum_action.setEnabled(True)