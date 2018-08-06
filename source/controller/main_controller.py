import sys
import os.path as path
sys.path.append(path.abspath("/Users/milhone/python_FabryPerot"))
sys.path.append(path.abspath("C:/Users/jason/python_FabryPerot"))
from PyQt5 import QtCore
from ..views import workers
from fabry.tools import images


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
        worker = workers.Worker(self._read_image_data, filename, bg_filename)
        worker.signals.result.connect(self.update_model_image_data)
        self.threadpool.start(worker)

    @staticmethod
    def _read_image_data(filename, bg_filename):
        print('calling the first open file')
        image_data = images.get_data(filename, color='b')
        print('calling the second open file')
        bg_image_data = images.get_data(bg_filename, color='b')

        return image_data, bg_image_data

    def update_model_image_data(self, incoming_data):
        print('im in the update portion')
        self.model.image = incoming_data[0]
        self.model.background = incoming_data[1]

        self.model.announce_update(registry='image_data')




