'''
FIBVID OFFICAL REPOSITORY
CREATED: 22 JUNE, 2015

DEVELOPERS
ABDUL HANNAN KHAN
'''

import sys
import cv2
import numpy as np
import random

from tile import *

from PyQt5.QtGui import (QPixmap, QImage, QKeyEvent, QCursor)
from PyQt5.QtWidgets import (QLabel, QWidget, QMenuBar, QMenu, QStatusBar,
                             QAction, QMainWindow, QFileDialog, QApplication)
from PyQt5.QtCore import (Qt, QCoreApplication)
from config import *

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.grid_size = GRID_SIZE

        #adjusting main window
        self.resize(TILES_WINDOW_WIDTH, TILES_WINDOW_HEIGHT)
        self.move(0, 0)
        self.setWindowTitle("Trainer")

        #initializing tiles

        self.addTiles(TILE_WIDTH, TILE_HEIGHT)

        #initializing menubar
        self.menubar = QMenuBar(self)

        #adding menu options
        self.grid_menu = QMenu(self.menubar)
        self.grid_menu.setTitle("Grid")

        self.model_menu = QMenu(self.menubar)
        self.model_menu.setTitle("Model")

        self.file_menu = QMenu(self.menubar)
        self.file_menu.setTitle("File")

        #adding file submenu options
        exit = QAction(self)
        exit.setText("Exit")
        exit.setShortcut('Alt+F4')
        exit.triggered.connect(self.exit)
        self.file_menu.addAction(exit)

        #adding grid submenu options
        g3 = QAction(self)
        g3.setText("3 X 3")
        g3.triggered.connect(self.toGrid3)
        g3.setShortcut("3")
        self.grid_menu.addAction(g3)

        g5 = QAction(self)
        g5.setText("5 X 5")
        g5.triggered.connect(self.toGrid5)
        g5.setShortcut("5")
        self.grid_menu.addAction(g5)

        g7 = QAction(self)
        g7.setText("7 X 7")
        g7.triggered.connect(self.toGrid7)
        g7.setShortcut("7")
        self.grid_menu.addAction(g7)

        g9 = QAction(self)
        g9.setText("9 X 9")
        g9.setShortcut("9")
        g9.triggered.connect(self.toGrid9)
        self.grid_menu.addAction(g9)

        #add model submenus
        re_train = QAction(self)
        re_train.setText("Retrain")
        re_train.setShortcut('Ctrl+R')
        re_train.triggered.connect(self.retrain)
        self.model_menu.addAction(re_train)


        #registering menus to menubar
        self.menubar.addAction(self.file_menu.menuAction())
        self.menubar.addAction(self.model_menu.menuAction())
        self.menubar.addAction(self.grid_menu.menuAction())

        #registering menubar
        self.menubar.move(0, 0)
        self.menubar.setDefaultUp(False)
        self.setMenuBar(self.menubar)

        #initializing and registering statusbar
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)

    def retrain(self):
        print("retrain")
        # to be implemented

    def exit(self):
        QCoreApplication.instance().quit()

    def toGrid3(self):
        self.changeGridSize(3)

    def toGrid5(self):
        self.changeGridSize(5)

    def toGrid7(self):
        self.changeGridSize(7)

    def toGrid9(self):
        self.changeGridSize(9)

    def changeGridSize(self, size):
        #change grid size to new size
        self.grid_size = size

        #redraw frames to get new look
        self.drawFrames()

    def addTiles(self, tile_width, tile_height):

        # initializing and registering centeral widget
        self.centeral_widget = QWidget(self)
        self.setCentralWidget(self.centeral_widget)

        #initialize tiles
        self.tiles = []

        #add tiles according to grid size
        for i in range(0, self.grid_size):
            self.tiles.append([])

            for j in range(0, self.grid_size):
                tile = Tile(self.centeral_widget)
                tile.move(TILES_MARGIN_LEFT *
                          (j + 1) + tile_width * j,
                          TILES_MARGIN_TOP * (i + 1) +
                          tile_height * i)
                tile.resize(tile_width, tile_height)
                self.tiles[i].append(tile)

    def drawFrames(self):

        #draw images in frames

        #initial width and height
        width = TILE_WIDTH
        height = TILE_HEIGHT

        if DYNAMIC_WINDOW_SCALING:
            #if dynamic scalling is available resize tiles
            # according to current window size
            window_width = self.centeral_widget.width()
            window_height = self.centeral_widget.height()
            (width, height) = reconfig_tile_geometery(
                window_width, window_height, self.grid_size)

        #add tile views for images
        self.addTiles(width, height)

        #read test image
        img = cv2.imread("fish.jpg")

        #resize test image
        img = cv2.resize(img, (width, height))

        #set test image in all tiles
        for i in range(0, self.grid_size):
            for j in range(0, self.grid_size):

                if random.random() < 0.5:
                    self.tiles[i][j].lable = 1
                else:
                    self.tiles[i][j].lable = 0
                self.tiles[i][j].image = img
                self.tiles[i][j].drawImage()

    def resizeEvent(self, event):
        self.drawFrames()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())