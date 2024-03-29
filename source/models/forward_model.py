from PyQt5 import QtCore
import numpy as np
from .base_model import BaseModel


class ForwardModel(BaseModel):

    def __init__(self, focal_length, etalon_spacing, finesse, pixel_size, wavelength_data=None):
        super(ForwardModel, self).__init__()
        wavelength_data = np.zeros((8,5))
        wavelength_data[0, :] = np.asarray([488.0, 1.0, 40.0, 0.3, 0.0])
        self.qmodel = QForwardModel(data=wavelength_data)
        self.L = focal_length
        self.d = etalon_spacing
        self.F = finesse
        self.pixel_size = pixel_size

        self.r = None
        self.model_ringsum = None

        self.update_registry = {'model_ringsum_update': list(),
                                }


class QForwardModel(QtCore.QAbstractTableModel):

    def __init__(self, data=None, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent=parent)
        self._data = data
        self.column_names = ['Wavelength (nm)', 'Amp (Counts)', 'mu', 'Ti (eV)', 'Velocity (km/s)']
        if self._data is None:
            self._data = np.zeros((8, 5))

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        if orientation == QtCore.Qt.Horizontal:
            return self.column_names[section]

        return QtCore.QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        # print('im in data() right now')
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        if not index.isValid():
            return QtCore.QVariant()

        row = index.row()
        column = index.column()

        try:
            value = self._data[row, column]
        except IndexError:
            return QtCore.QVariant()

        return QtCore.QVariant(str(value))

    def setData(self, index, value, role):
        row = index.row()
        column = index.column()

        try:
            value = np.float64(value)
        except ValueError:
            return False

        try:
            self._data[row, column] = value
            return True
        except IndexError:
            # Not sure what I should do here other than exit gracefully
            # Really don't know why I would be here in the first place
            return False

    def rowCount(self, parent=QtCore.QModelIndex):
        return self._data.shape[0]

    def columnCount(self, parent=QtCore.QModelIndex):
        return self._data.shape[1]

    # didn't really see this in a lot of stack overflow answers, but was the key to having editable cells
    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable

    def retrieve_data(self):
        return self._data

    def load_data_from_csv(self, filename):
        input_data = np.genfromtxt(filename, dtype=np.float64, delimiter=',',
                                   filling_values=0.0, max_rows=8)
        n, m = input_data.shape

        if n != 8:
            zero_pad = np.zeros((8-n, 5))
            input_data = np.vstack((input_data, zero_pad))
        self._data = input_data
        self.dataChanged.emit(self.index(0, 0), self.index(7, 4), [QtCore.Qt.DisplayRole])

    def save_data_to_csv(self, filename):
        column_names = self.column_names
        header = ",".join(column_names)
        np.savetxt(filename, self._data, delimiter=',', header=header)


