'''
FIBVID OFFICAL REPOSITORY
CREATED: 22 JUNE, 2015

DEVELOPERS
ABDUL HANNAN KHAN
'''

import numpy as np
import cv2
from config import *

from PyQt5.QtWidgets import (QLabel, QApplication)
from PyQt5.QtGui import (QImage, QPixmap, QCursor)
from PyQt5.QtCore import (Qt)


class Tile(QLabel):
    def __init__(self, widget):
        super().__init__(widget)
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        self.lable = 1 - self.lable
        self.drawImage()

    def enterEvent(self, QEvent):

        # backup original image
        img = self.image

        # create a small hover effect
        self.image = np.uint8(img * 0.9)

        # draw image
        self.drawImage()

        # keep original image
        self.image = img

        #set hover cursor
        QApplication.setOverrideCursor(QCursor(Qt.OpenHandCursor))

    def leaveEvent(self, QEvent):

        #draw original image
        self.drawImage()

        #remove hover cursor
        QApplication.restoreOverrideCursor()

    def flag(self):

        (width, height, depth) = np.shape(self.image)

        # set a random color lable to image
        if (self.lable == 1):
            self.image[:TILE_LABLE_SIZE, -TILE_LABLE_SIZE:] = \
                [255, 0, 0]
        else:
            self.image[:TILE_LABLE_SIZE, -TILE_LABLE_SIZE:] = \
                [0, 255, 0]

        return self.image

    def drawImage(self):

        (height, width, depth) = np.shape(self.image)

        qmap = QPixmap.fromImage(QImage(self.flag(), \
                                                width, height,
                                                width * depth,
                                                QImage.Format_RGB888))

        self.setPixmap(qmap)
