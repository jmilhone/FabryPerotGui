from PyQt5 import QtCore
import numpy as np


class ForwardModel(object):

    def __init__(self, focal_length, etalon_spacing, finesse, wavelength_data=None):
        super(ForwardModel, self).__init__()
        self.model = QForwardModel(data=wavelength_data)
        self.L = focal_length
        self.d = etalon_spacing
        self.F = finesse


class QForwardModel(QtCore.QAbstractTableModel):

    def __init__(self, data=None, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent=parent)
        self._data = data
        self.column_names = ['Wavelength (nm)', 'Amp (Counts)', 'Velocity (km/s)']
        if self._data is None:
            self._data = np.zeros((8, 3))

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        if orientation == QtCore.Qt.Horizontal:
            return self.column_names[section]

        return QtCore.QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
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

        # This doesn't work for me, stupid stack overflow
        # try:
        #     print(value)
        #     value = value.toPyObject()
        #     print(value)
        # except AttributeError:
        #     # I guess if I accept PySide, this should be handled differently, but I don't really care at this point
        #     value = np.nan

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
