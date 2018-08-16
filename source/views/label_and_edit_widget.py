from __future__ import division, print_function
from PyQt5 import QtWidgets, QtCore

accepted_types = {'QDoubleSpinBox': QtWidgets.QDoubleSpinBox,
                  'QSpinBox': QtWidgets.QSpinBox,
                  }


class QLabelAndSpinBox(QtWidgets.QWidget):
    valueChanged = QtCore.pyqtSignal([float], [int])

    def __init__(self, label, edit_type='QDoubleSpinBox', default_value=None, default_range=None, precision=None):

        super(QLabelAndSpinBox, self).__init__()
        # self.setStyleSheet("padding: 0 0 0 0")
        self.hbox = QtWidgets.QHBoxLayout()

        self.label = QtWidgets.QLabel()

        if edit_type in accepted_types:
            self.edit = accepted_types[edit_type]()
        else:
            raise ValueError('Accepted types are QDoubleSpinBox and QSpinBox')

        self.edit.setKeyboardTracking(False)

        self.label.setText(str(label))
        if precision is not None:
            self.edit.setDecimals(precision)

        if default_range is not None and len(default_range) >= 2:
            self.edit.setRange(default_range[0], default_range[1])

        if default_value is not None:
            self.edit.setValue(default_value)

        self.edit.valueChanged.connect(self.on_value_change)

        self.hbox.addWidget(self.label)
        self.hbox.addWidget(self.edit)
        self.hbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.hbox)

    @QtCore.pyqtSlot(int)
    @QtCore.pyqtSlot(float)
    def on_value_change(self, value):
        self.valueChanged.emit(value)

    def setValue(self, value):
        self.edit.setValue(value)

    def value(self):
        return self.edit.value()
