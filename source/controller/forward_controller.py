from __future__ import division, print_function
import sys
import os.path as path
sys.path.append(path.abspath("/Users/milhone/python_FabryPerot"))
sys.path.append(path.abspath("C:/Users/jason/python_FabryPerot"))
from ..models.forward_model import ForwardModel
from ..models.image_model import FabryPerotModel
from ..views.workers import Worker
from PyQt5 import QtCore
import numpy as np
from fabry.core.models import forward_model


class ForwardController(object):
    def __init__(self, fp_forward_model, image_model):
        """

        :param fp_forward_model: fabry perot forward q instance
        :type fp_forward_model: ForwardModel
        :param image_model: fabry perot image model
        :type image_model: FabryPerotModel
        """
        super(ForwardController, self).__init__()
        self.fp_forward_model = fp_forward_model
        self.image_model = image_model
        self.threadpool = QtCore.QThreadPool()

    def calculate_model_spectrum(self, L, d, F):
        self.image_model.status = 'Calculating Model Ringsum'
        self.image_model.announce_update(registry='status')

        self.fp_forward_model.L = L
        self.fp_forward_model.d = d
        self.fp_forward_model.F = F
        pixel_size = self.fp_forward_model.pixel_size
        L /= pixel_size
        data = self.fp_forward_model.qmodel.retrieve_data()
        r = self.image_model.r
        if r is None:
            r = np.linspace(0, 1000, 1001)  # in pixels

        wavelengths = []
        amplitudes = []
        velocities = []
        temperatures = []
        masses = []

        for row in data:
            if all(x > 0.0 for x in row[0:4]):
                # we have valid wavelengths and amplitudes
                wavelengths.append(row[0])
                amplitudes.append(row[1])
                masses.append(row[2])
                temperatures.append(row[3])
                velocities.append(row[4]*1000)
        if len(wavelengths):
            worker = Worker(self._calculate_model_spectrum, r, L, d, F, wavelengths, masses, amplitudes, temperatures,
                            velocities, nlambda=2000)
            worker.signals.result.connect(self.update_model_ringsum_data)
            self.threadpool.start(worker)

    @staticmethod
    def _calculate_model_spectrum(r, L, d, F, w0, mu, amp, temp, v, nlambda=1000):
        signal = forward_model(r, L, d, F, w0, mu, amp, temp, v, nlambda=nlambda)
        return r, signal

    def update_model_ringsum_data(self, incoming_data):
        self.fp_forward_model.r = incoming_data[0]
        self.fp_forward_model.model_ringsum = incoming_data[1]
        self.fp_forward_model.announce_update(registry='model_ringsum_update')
        self.image_model.status = 'IDLE'
        self.image_model.announce_update(registry='status')

    def update_effective_pixel_size(self):
        pixel_size = self.image_model.pixel_size
        super_pixel_size = self.image_model.super_pixel
        self.fp_forward_model.pixel_size = pixel_size * super_pixel_size



