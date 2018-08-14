import sys
import os.path as path
import numpy as np
sys.path.append(path.abspath("/Users/milhone/python_FabryPerot"))
sys.path.append(path.abspath("C:/Users/jason/python_FabryPerot"))
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from PyQt5 import QtCore
from ..views import workers
from fabry.tools import images, file_io
from fabry.core import ringsum


class MainController(object):
    """

    :param model: Model object
    :type model: source.models.model.FabryPerotModel
    """

    def __init__(self, model):
        super(MainController, self).__init__()
        self.model = model
        self.threadpool = QtCore.QThreadPool()

    def read_image_data(self, filename, bg_filename, npix=None):
        """Reads in image via helper function _read_image_data

        :param filename: path to image file
        :type filename: str
        :param bg_filename: path to background image file
        :type bg_filename: str
        """
        self.model.image_name = filename
        self.model.background_name = bg_filename
        self.model.super_pixel = npix
        # Reset ring sum data because we are reopening the image
        self.model.center = None
        self.model.r = None
        self.model.ringsum = None
        self.model.ringsum_err = None

        self.change_model_status_and_announce('Reading Images')
        worker = workers.Worker(self._read_image_data, filename, bg_filename, npix=npix)
        worker.signals.result.connect(self.update_model_image_data)
        self.threadpool.start(worker)

    @staticmethod
    def _read_image_data(filename, bg_filename, npix=None):
        """Reads in both image and background image data

        :param filename: path to image file
        :type filename: str
        :param bg_filename: path to background image file
        :type bg_filename: str
        :return: image and background 2D numpy arrays
        :rtype: tuple (np.ndarray, np.ndarray)
        """
        image_data = images.get_data(filename, color='b')
        bg_image_data = images.get_data(bg_filename, color='b')

        if npix is not None and npix > 1:
            image_data = ringsum.super_pixelate(image_data, npix=npix)
            bg_image_data = ringsum.super_pixelate(bg_image_data, npix=npix)
        return image_data, bg_image_data

    def update_model_image_data(self, incoming_data):
        """Updates self.model.image and self.model.background with incoming data and calls
        self.model.announce_update for the image data registry

        :param incoming_data: image and background image 2D numpy arrays
        :type incoming_data: tuple (np.ndarray, np.ndarray)
        """
        self.model.image = incoming_data[0]
        self.model.background = incoming_data[1]

        self.model.announce_update(registry='image_data')
        self.change_model_status_and_announce('IDLE')

    def find_center(self, x_guess, y_guess):
        """

        :param x_guess:
        :param y_guess:
        :return:
        """
        self.change_model_status_and_announce('Locating Center')
        worker = workers.Worker(self._find_center, self.model.image, x_guess, y_guess)
        worker.signals.result.connect(self.update_center)
        self.threadpool.start(worker)

    @staticmethod
    def _find_center(data, x_guess, y_guess):
        """

        :param data:
        :param x_guess:
        :param y_guess:
        :return:
        """
        x0, y0 = ringsum.locate_center(data, xguess=x_guess, yguess=y_guess, printit=True)
        return x0, y0

    def update_center(self, incoming_data):
        """

        :param incoming_data:
        :return:
        """
        self.model.center = incoming_data
        self.model.announce_update(registry='image_data')
        self.change_model_status_and_announce('IDLE')

    def get_ringsum(self, binsize=0.1):
        """

        :return:
        """
        if self.model.center is None:
            return
        self.model.binsize = binsize
        self.change_model_status_and_announce('Performing ring sum')
        worker = workers.Worker(self._get_ringsum, self.model.image, self.model.background, *self.model.center,
                                binsize=binsize)
        worker.signals.result.connect(self.update_ringsum)
        self.threadpool.start(worker)

    @staticmethod
    def _get_ringsum(data, bg_data, x0, y0, binsize=0.1):
        """

        :param data:
        :param bg_data:
        :param x0:
        :param y0:
        :return:
        """
        r, rs, rs_sd = ringsum.ringsum(data, x0, y0, quadrants=False, use_weighted=False, binsize=binsize)
        _, rs_bg, rs_sd_bg = ringsum.ringsum(bg_data, x0, y0, quadrants=False, use_weighted=False, binsize=binsize)

        rs -= rs_bg
        rs_sd = np.sqrt(rs_sd**2 + rs_sd_bg**2 + (0.01*rs)**2)

        return r, rs, rs_sd

    def update_ringsum(self, incoming_data):
        """

        :param incoming_data:
        :return:
        """
        self.model.r = incoming_data[0]
        self.model.ringsum = incoming_data[1]
        self.model.ringsum_err = incoming_data[2]

        self.model.announce_update(registry="ringsum_data")
        self.change_model_status_and_announce('IDLE')

    def change_model_status_and_announce(self, status):
        """

        :param status:
        :return:
        """
        self.model.status = status
        self.model.announce_update(registry='status')

    def save_model_data(self, output_filename):
        """

        :param output_filename:
        :return:
        """
        output_dict = self.model.to_dict()
        file_io.dict_2_h5(output_filename, output_dict)

