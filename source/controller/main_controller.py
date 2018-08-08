import sys
import os.path as path
import numpy as np
sys.path.append(path.abspath("/Users/milhone/python_FabryPerot"))
sys.path.append(path.abspath("C:/Users/jason/python_FabryPerot"))
from PyQt5 import QtCore
from ..views import workers
from fabry.tools import images
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

    def read_image_data(self, filename, bg_filename):
        """Reads in image via helper function _read_image_data

        :param filename: path to image file
        :type filename: str
        :param bg_filename: path to background image file
        :type bg_filename: str
        """
        # self.model.status = 'Reading Images'
        # self.model.announce_update(registry='status')
        self.change_model_status_and_announce('Reading Images')
        worker = workers.Worker(self._read_image_data, filename, bg_filename)
        worker.signals.result.connect(self.update_model_image_data)
        self.threadpool.start(worker)

    @staticmethod
    def _read_image_data(filename, bg_filename):
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
        # self.model.status = 'IDLE'
        # self.model.announce_update(registry='status')

    def find_center(self, x_guess, y_guess):
        # self.model.status = 'Locating Center'
        # self.model.announce_update(registry='status')
        self.change_model_status_and_announce('Locating Center')
        worker = workers.Worker(self._find_center, self.model.image, x_guess, y_guess)
        worker.signals.result.connect(self.update_center)
        self.threadpool.start(worker)

    @staticmethod
    def _find_center(data, x_guess, y_guess):
        x0, y0 = ringsum.locate_center(data, xguess=x_guess, yguess=y_guess, printit=True)
        return x0, y0

    def update_center(self, incoming_data):
        self.model.center = incoming_data
        self.model.announce_update(registry='image_data')
        self.change_model_status_and_announce('IDLE')

    def get_ringsum(self):
        if self.model.center is None:
            return
        # self.model.status = 'Performing ring sum'
        # self.model.announce_update(registry='status')
        self.change_model_status_and_announce('Performing ring sum')
        worker = workers.Worker(self._get_ringsum, self.model.image, self.model.background, *self.model.center)
        worker.signals.result.connect(self.update_ringsum)
        self.threadpool.start(worker)

    @staticmethod
    def _get_ringsum(data, bg_data, x0, y0):
        r, rs, rs_sd = ringsum.ringsum(data, x0, y0, quadrants=False, use_weighted=False)
        _, rs_bg, rs_sd_bg = ringsum.ringsum(bg_data, x0, y0, quadrants=False, use_weighted=False)

        rs -= rs_bg
        rs_sd = np.sqrt(rs_sd**2 + rs_sd_bg**2 + (0.01*rs)**2)

        return r, rs, rs_sd

    def update_ringsum(self, incoming_data):
        self.model.r = incoming_data[0]
        self.model.ringsum = incoming_data[1]
        self.model.ringsum_err = incoming_data[2]

        self.model.announce_update(registry="ringsum_data")
        self.change_model_status_and_announce('IDLE')

    def change_model_status_and_announce(self, status):
        self.model.status = status
        self.model.announce_update(registry='status')

