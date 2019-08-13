from __future__ import print_function, absolute_import, division
from PyQt5 import QtWidgets
from .matplotlib_widget import MatplotlibWidget
# from source.models.forward_model import ForwardModel
from ..models.forward_model import ForwardModel
from .label_and_edit_widget import QLabelAndSpinBox
from ..controller.forward_controller import ForwardController
# import matplotlib.pyplot as plt
# from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np


class MainWindow(QtWidgets.QMainWindow):
    """

    :param model: data qmodel
    :type model: source.models.base_model.FabryPerotModel
    :param controller: controller
    :type controller: source.controller.main_controller.MainController
    :attribute plot_window: matplotlib window with navigation toolbar
    :type image_plot_window: source.views.matplotlib_widget.MatplotlibWidget
    """

    def __init__(self, model, controller, filename=None, bg_filename=None):
        super(MainWindow, self).__init__()
        self.model = model
        self.controller = controller
        self.cb = None
        self.legend = None
        # set up menu bar and qactions
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu('File')

        self.open_image_action = QtWidgets.QAction('Open images...', self)
        self.save_ringsum_action = QtWidgets.QAction('Save ringsum data...', self)
        self.open_wavelength_model_input_action = QtWidgets.QAction("Open wavelength model...", self)
        self.save_wavelength_model_action = QtWidgets.QAction("Save wavelength model as...", self)

        self.tabs = QtWidgets.QTabWidget()

        self.image_plot_window = MatplotlibWidget()
        self.ringsum_plot_window = MatplotlibWidget()
        self.central_widget = QtWidgets.QWidget(self)
        self.hbox = QtWidgets.QHBoxLayout()

        self.image_sidebar_vbox = QtWidgets.QVBoxLayout()
        self.forward_model_sidebar_vbox = QtWidgets.QVBoxLayout()
        self.sidebar = QtWidgets.QVBoxLayout()

        self.x0_entry = QLabelAndSpinBox('X Center Guess', edit_type='QDoubleSpinBox', default_range=(0.0, 1e4),
                                         default_value=0.0)
        self.y0_entry = QLabelAndSpinBox('Y Center Guess', edit_type='QDoubleSpinBox', default_range=(0.0, 1e4),
                                         default_value=0.0)
        self.binsize_entry = QLabelAndSpinBox('Binsize (px)', edit_type='QDoubleSpinBox', default_range=(0.01, 2.0),
                                              default_value=0.1)
        self.npix_entry = QLabelAndSpinBox('Super Pixel Size (px)', edit_type='QSpinBox', default_range=(1, 10),
                                           default_value=1)
        self.pixel_size_entry = QLabelAndSpinBox('Pixel Size (mm)', edit_type='QDoubleSpinBox',
                                                 default_range=(0.0001, 0.1), default_value=0.00586, precision=6)
                                                 #default_range=(0.0001, 0.1), default_value=0.004, precision=6)
        self.display_image_button = QtWidgets.QPushButton()
        self.find_center_button = QtWidgets.QPushButton()
        self.calculate_forward_button = QtWidgets.QPushButton()

        self.button_box = QtWidgets.QHBoxLayout()

        self.center_label = QtWidgets.QLabel()

        self.get_ringsum_button = QtWidgets.QPushButton()

        self.status_label = QtWidgets.QLabel()
        self.forward_model = ForwardModel(75.0, 0.8831, 22.0, 0.00586)
        #self.forward_model = ForwardModel(150.0, 0.8836, 22.0, 0.004)
        self.forward_controller = ForwardController(self.forward_model, self.model)
        # self.forward_model.qmodel.save_data_to_csv("test_input.csv")
        self.table_view = QtWidgets.QTableView()
        self.table_view.setModel(self.forward_model.qmodel)

        self.finesse = QLabelAndSpinBox('Finesse', edit_type='QDoubleSpinBox', default_value=22,
                                        default_range=(1.0, 30.0))
        self.etalon_spacing = QLabelAndSpinBox('Etalon Spacing (mm)', edit_type='QDoubleSpinBox', default_value=0.8836,
                                               default_range=(0.1, 5.0), precision=9)
        self.focal_length = QLabelAndSpinBox('Focal Length (mm)', edit_type='QDoubleSpinBox', default_value=75.0,
                                             default_range=(1.0, 1000.0), precision=4)

        self.image_options_group = QtWidgets.QGroupBox("Image Options")
        self.image_options_group.setObjectName('OptionsGroup')
        self.forward_model_options_group = QtWidgets.QGroupBox("Forward Model Options")
        self.forward_model_options_group.setObjectName('ForwardGroup')

        # self.options_group.setStyleSheet("QGroupBox#OptionsGroup {border: 1px solid gray; border-radius: 3px;}; QGroupBox::title {subcontrol-origin: margin; left: 3px; padding: 3 0 3 0;}")
        self.image_options_group.setStyleSheet(
            "QGroupBox::title {subcontrol-origin: margin; left: 3px; bottom: 5 px; padding: 3 0 3 0;} QGroupBox#OptionsGroup {border: 1px solid gray; border-radius: 3px; font-weight: bold}")
        self.forward_model_options_group.setStyleSheet(
            "QGroupBox::title {subcontrol-origin: margin; left: 3px; bottom: 5 px; padding: 3 0 3 0;} QGroupBox#ForwardGroup {border: 1px solid gray; border-radius: 3px; font-weight: bold}")
        self.setStyleSheet("padding: 2 0 2 0;")

        # Put all gui elements before this line!
        self.init_UI()

        self.button_list = [
            self.display_image_button,
            self.find_center_button,
            self.get_ringsum_button,
            self.calculate_forward_button,
        ]

        self.action_list = [
            self.open_image_action,
            self.save_ringsum_action,
            self.open_wavelength_model_input_action,
            self.save_wavelength_model_action,
        ]

        # Subscribe functions for updates in q
        self.model.subscribe_update_func(self.display_image_data, registry='image_data')
        self.model.subscribe_update_func(self.update_initial_center_entry, registry='image_data')
        self.model.subscribe_update_func(self.plot_ringsum, registry='ringsum_data')
        self.model.subscribe_update_func(self.update_center_label, registry='image_data')
        self.model.subscribe_update_func(self.update_status_label, registry='status')
        self.model.subscribe_update_func(self.enable_save_ringsum, registry='ringsum_data')
        self.model.subscribe_update_func(self.forward_controller.update_effective_pixel_size, registry='image_data')
        self.forward_model.subscribe_update_func(self.plot_ringsum, registry='model_ringsum_update')

        # Set up PyQt signals for GUI Events
        self.find_center_button.clicked.connect(self.find_center)
        self.get_ringsum_button.clicked.connect(self.find_ringsum)
        self.open_image_action.triggered.connect(self.open_images_dialog)
        self.display_image_button.clicked.connect(self.display_image_button_pressed)
        self.calculate_forward_button.clicked.connect(self.calculate_model_spectrum)
        self.save_ringsum_action.triggered.connect(self.save_ringsum_to_file)
        self.open_wavelength_model_input_action.triggered.connect(self.open_wavelength_model)
        self.save_wavelength_model_action.triggered.connect(self.save_wavelength_model)

        if filename:
            self.controller.read_image_data(filename, bg_filename, npix=self.npix_entry.value(),
                                            px_size=self.pixel_size_entry.value())

    def init_UI(self):
        """

        :return:
        """
        # options for qactions
        self.open_image_action.setCheckable(False)
        self.save_ringsum_action.setCheckable(False)
        self.save_ringsum_action.setEnabled(False)
        self.open_wavelength_model_input_action.setCheckable(False)

        # add actions to menu bar
        self.file_menu.addAction(self.open_image_action)
        self.file_menu.addAction(self.save_ringsum_action)
        self.file_menu.addAction(self.open_wavelength_model_input_action)
        self.file_menu.addAction(self.save_wavelength_model_action)

        self.display_image_button.setText("Display Image")

        self.find_center_button.setText("Find Center")
        self.center_label.setText("Center: ")

        self.get_ringsum_button.setText("Find Ringsum")
        self.get_ringsum_button.setDisabled(True)

        self.calculate_forward_button.setText('Calculate Forward Model')

        self.status_label.setText("Status: IDLE")

        self.button_box.addWidget(self.display_image_button)
        self.button_box.addWidget(self.find_center_button)
        self.button_box.addWidget(self.get_ringsum_button)

        self.image_sidebar_vbox.addWidget(self.pixel_size_entry)
        self.image_sidebar_vbox.addWidget(self.npix_entry)
        self.image_sidebar_vbox.addWidget(self.x0_entry)
        self.image_sidebar_vbox.addWidget(self.y0_entry)
        self.image_sidebar_vbox.addWidget(self.center_label)
        self.image_sidebar_vbox.addWidget(self.binsize_entry)
        self.image_sidebar_vbox.addLayout(self.button_box)
        self.image_options_group.setLayout(self.image_sidebar_vbox)

        self.forward_model_sidebar_vbox.addWidget(self.finesse)
        self.forward_model_sidebar_vbox.addWidget(self.etalon_spacing)
        self.forward_model_sidebar_vbox.addWidget(self.focal_length)
        self.forward_model_sidebar_vbox.addWidget(self.table_view)
        self.forward_model_sidebar_vbox.addWidget(self.calculate_forward_button)
        self.forward_model_options_group.setLayout(self.forward_model_sidebar_vbox)

        self.sidebar.addStretch(1)
        self.sidebar.addWidget(self.image_options_group)
        self.sidebar.addWidget(self.forward_model_options_group)
        self.sidebar.addStretch(10)
        self.sidebar.addWidget(self.status_label)

        self.tabs.addTab(self.image_plot_window, "Image")
        self.tabs.addTab(self.ringsum_plot_window, "Ring Sum")

        self.hbox.addWidget(self.tabs, 10)
        self.hbox.addLayout(self.sidebar, 6)
        self.central_widget.setLayout(self.hbox)
        self.setCentralWidget(self.central_widget)

        self.table_view.resizeColumnsToContents()

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
            self.x0_entry.setValue(nx / 2.0)
            # self.x0_entry.setValue(2985.7)
        if self.y0_entry.value() == 0.0:
            self.y0_entry.setValue(ny / 2.0)
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
        if self.legend is not None:
            self.legend.remove()
            self.legend = None

        r = self.model.r
        sig = self.model.ringsum
        sig_sd = self.model.ringsum_err

        self.ringsum_plot_window.axs.cla()

        # if self.cb is not None:
        #     self.cb.remove()
        #     self.cb = None

        unit_string = ""
        if all(x is not None for x in (r, sig, sig_sd)):
            n = int(np.log10(sig.max()))
            #print('divisor', n)
            divisor = 10.0 ** n
            unit_string = "(x$10^{" + "{0}".format(n) + "}$)"
            self.ringsum_plot_window.axs.errorbar(r, sig / divisor, yerr=sig_sd / divisor, color='C0',
                                                  label='Image Ringsum')

        r_model = self.forward_model.r
        ringsum_model = self.forward_model.model_ringsum
        if r_model is not None and ringsum_model is not None:
            self.ringsum_plot_window.axs.plot(r_model, ringsum_model, color='C1', label='Model Ringsum')
        self.ringsum_plot_window.axs.set_xlabel("R (px)")
        self.ringsum_plot_window.axs.set_ylabel("Counts " + unit_string)
        self.ringsum_plot_window.axs.axis('tight')

        if len(self.ringsum_plot_window.axs.get_lines()):
            self.legend = self.ringsum_plot_window.axs.legend()

        self.ringsum_plot_window.toolbar.update()
        self.ringsum_plot_window.toolbar.push_current()
        self.ringsum_plot_window.figure.tight_layout()
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
            # require an image with rings
            return

        filename = dlg.selectedFiles()[0]

        dlg = QtWidgets.QFileDialog(self, 'Pick a Background Image')
        dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dlg.setNameFilters(["Images (*.nef)", "Numpy (*.npy)", "HDF5 (*.h5)"])
        dlg.selectNameFilter("Images (*.nef)")

        # Dont need a background to run
        bg_filename = None
        if dlg.exec_():
            bg_filename = dlg.selectedFiles()[0]

        npix = self.npix_entry.value()
        px_size = self.pixel_size_entry.value()
        self.controller.read_image_data(filename, bg_filename, npix=npix, px_size=px_size)

    def display_image_button_pressed(self, checked):
        fname = self.model.image_name
        bg_fname = self.model.background_name
        npix = self.model.super_pixel
        px_size = self.model.pixel_size
        data = self.model.image
        user_npix = self.npix_entry.value()
        user_px_size = self.pixel_size_entry.value()

        if fname and bg_fname:
            # we have file names
            if data is None or user_npix != npix or user_px_size != px_size:
                # we either don't have image data or we need to reopen for super pixelate
                self.controller.read_image_data(fname, bg_fname, npix=user_npix, px_size=user_px_size)
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
        enable = True
        if new_status != 'IDLE':
            enable = False
        self.toggle_all_buttons(enable)
        self.toggle_all_actions(enable)

        status_str = "Status: {0:s}".format(new_status)
        self.status_label.setText(status_str)

    def toggle_all_buttons(self, enabled):
        """

        :param enabled:
        :return:
        """
        for button in self.button_list:
            if button == self.get_ringsum_button and self.model.center is None:
                button.setEnabled(False)
            else:
                button.setEnabled(enabled)

    def toggle_all_actions(self, enabled):
        """

        :param enabled:
        :return:
        """
        for action in self.action_list:
            if action == self.save_ringsum_action and self.model.ringsum is None:
                action.setEnabled(False)
            else:
                action.setEnabled(enabled)

    def enable_save_ringsum(self):
        self.save_ringsum_action.setEnabled(True)

    def calculate_model_spectrum(self):
        L = self.focal_length.value()
        d = self.etalon_spacing.value()
        F = self.finesse.value()
        self.forward_controller.calculate_model_spectrum(L, d, F)

    def save_ringsum_to_file(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Ringsum As", "", "HDF5 (*.h5)")
        if filename:
            self.controller.save_image_model_data(filename)

    def open_wavelength_model(self, checked):
        dlg = QtWidgets.QFileDialog(self, 'Pick a Wavelength Model File')
        dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dlg.setNameFilters(["CSV (*.csv)", "Text (*.txt)"])
        dlg.selectNameFilter("CSV (*.csv)")

        if dlg.exec_():
            filename = dlg.selectedFiles()[0]
            self.forward_model.qmodel.load_data_from_csv(filename)

    def save_wavelength_model(self, checked):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, caption='Save wavelength model as',
                                                            filter="Text File (*.csv *.txt)")
        if filename != '':
            self.forward_model.qmodel.save_data_to_csv(filename)

