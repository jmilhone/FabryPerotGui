from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QSizePolicy, QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from matplotlib import rcParams


class MatplotlibWidget(QWidget):
    def __init__(self, parent=None,
                 width=4, height=3):
        QWidget.__init__(self, parent)
        super(MatplotlibWidget, self).__init__()

        self.figure, self.axs = plt.subplots(figsize=(width, height))

        self.canvas = Canvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)
        self.setParent(parent)
        super(MatplotlibWidget, self).setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)
        super(MatplotlibWidget, self).updateGeometry()

    def sizeHint(self):
        return QSize(*self.canvas.get_width_height())

    def minimumSizeHint(self):
        return QSize(10, 10)


