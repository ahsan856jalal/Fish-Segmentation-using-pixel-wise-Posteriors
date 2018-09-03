'''
FIBVID OFFICAL REPOSITORY
CREATED: 21 JUNE, 2015

DEVELOPERS
ABDUL HANNAN KHAN
SYED HASSAAN TAUQEER
'''

import sys
import cv2
import numpy as np
from pymongo import MongoClient

from PyQt5.QtGui import (QPixmap, QImage, QKeyEvent, QCursor)
from PyQt5.QtWidgets import (QLabel, QWidget, QMenuBar, QMenu, QStatusBar,
                             QAction, QMainWindow, QFileDialog, QApplication, QSlider, QActionGroup)
from PyQt5.QtCore import (Qt, QRect, QPoint)
from config import *
from augumented_qt import *

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        #adjusting main window
        self.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
        self.move(0, 0)

        #setting scaling factor = 1
        self.zoom = 1

        #initializing and registering centeral widget
        self.centeral_widget = QWidget(self)
        self.setCentralWidget(self.centeral_widget)

        #initializing frame view
        self.frame_panel = DLabel(self.centeral_widget, self)
        # position frame panel
        self.frame_panel.move(FRAME_MARGIN_LEFT, FRAME_MARGIN_TOP)

        # set initial image
        self.frame_panel.setPixmap(QPixmap("initial.png"))

        #fur testing
        self.frame_panel.content = cv2.imread("initial.png")

        # enabling custom context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)

        #initializing menubar
        self.menubar = QMenuBar(self)

        #adding menu options
        self.file_menu = QMenu(self.menubar)
        self.zoom_menu = QMenu(self.menubar)
        self.marker_menu = QMenu(self.menubar)
        self.bounding_boxes = QMenu(self.menubar)

        #registering menubar
        self.menubar.move(0, 0)
        self.menubar.setDefaultUp(False)
        self.setMenuBar(self.menubar)

        #initializing and registering statusbar
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)

        #add permanent frame lable to statusbar
        self.statusbar.frame_lable = QLabel(self)
        self.statusbar.frame_lable.setText("")
        self.statusbar.frame_lable.resize(100, 50)
        self.statusbar.frame_lable.move(DEFAULT_WINDOW_WIDTH - 100, DEFAULT_WINDOW_HEIGHT - 37)

        # set initail status tip
        self.statusbar.setStatusTip("Please choose a video file to begin")

        self.initialize_submenus()

        #assign visual texts to window, menus and submenus
        self.setTexts()

        #initailize video path
        self.vid_path = ""
        self.vid = False

        #adding slider for quick seek
        self.slider = QSlider(self.centeral_widget)

        #setting slider geometery
        self.slider.resize(DEFAULT_WINDOW_WIDTH - SLIDER_MARGINS * 2, SLIDER_HEIGHT)
        self.slider.move(SLIDER_MARGINS, DEFAULT_WINDOW_HEIGHT - STATUSBAR_HEIGHT - SLIDER_HEIGHT - SLIDER_MARGINS)

        #setting orientation
        self.slider.setOrientation(Qt.Horizontal)

        #connecting mouse event
        self.slider.valueChanged.connect(self.moveSliderToClickedPosition)
        self.slider.setDisabled(True)

        # initialize context menu
        self.initContextMenu()

        # initializing mongo client and db
        self.database_client = MongoClient()
        self.db = self.database_client.fish

        # initializing collection
        self.collection = False


    def initContextMenu(self):

        # initialize custom context menu and submenu
        self.context_menu = QMenu(self)
        self.context_sub_menu = QMenu('Class', self)

        # create a delete action
        self.delete_action = QAction('Delete', self)
        self.delete_action.triggered.connect(self.frame_panel.deleteMarker)

        # create get lable action
        self.ask_lable = QAction('Ask Lable', self)
        self.ask_lable.triggered.connect(self.frame_panel.getLable)

        # adding dictionary for reverse search
        self.classes = {}

        # initializing class group
        self.class_group = QActionGroup(self)

        # adding submenu actions

        for item in CONFIGURED_CLASSES:
            self.classes[item] = QAction(item, self)
            self.classes[item].setCheckable(True)
            self.class_group.addAction(self.classes[item])

        # connecting group to handlers and setting default class
        self.class_group.triggered.connect(self.frame_panel.toggleMarkerClass)
        self.classes[CONFIGURED_CLASSES[0]].setChecked(True)

        # add delete action to menu
        self.context_menu.addAction(self.delete_action)

        # add ask lable action to menu
        self.context_menu.addAction(self.ask_lable)

        # add class actions to submenu
        self.context_sub_menu.addActions(self.class_group.actions())

        # regester submenu to menu
        self.context_menu.addMenu(self.context_sub_menu)

    def initialize_submenus(self):

        #intializing open submenu
        self.open_submenu = QAction(self)
        self.open_submenu.setShortcut('Ctrl+F')
        self.open_submenu.setStatusTip("Open")
        self.open_submenu.triggered.connect(self.selectFile)

        # intializing export submenu
        self.export_submenu = QAction(self)
        self.export_submenu.setShortcut('Ctrl+E')
        self.export_submenu.setStatusTip("Export")
        self.export_submenu.triggered.connect(self.exportImages)
        self.export_submenu.setDisabled(True)

        # intializing export submenu
        self.init_submenu = QAction(self)
        self.init_submenu.setShortcut('Ctrl+I')
        self.init_submenu.setStatusTip("Initialize")
        self.init_submenu.triggered.connect(self.initializeWithAlgorithm)
        self.init_submenu.setDisabled(True)

        #initializing options for zoom menu
        self.p50_submenu = QAction(self)
        self.p50_submenu.setStatusTip("50%")
        self.p50_submenu.setCheckable(True)
        self.p50_submenu.val = 0.5

        self.p100_submenu = QAction(self)
        self.p100_submenu.setStatusTip("100%")
        self.p100_submenu.setCheckable(True)
        self.p100_submenu.val = 1.0

        self.p150_submenu = QAction(self)
        self.p150_submenu.setStatusTip("150%")
        self.p150_submenu.setCheckable(True)
        self.p150_submenu.val = 1.5

        self.p200_submenu = QAction(self)
        self.p200_submenu.setStatusTip("200%")
        self.p200_submenu.setCheckable(True)
        self.p200_submenu.val = 2.0

        self.zoom_group = QActionGroup(self)
        self.zoom_group.addAction(self.p50_submenu)
        self.zoom_group.addAction(self.p100_submenu)
        self.zoom_group.addAction(self.p150_submenu)
        self.zoom_group.addAction(self.p200_submenu)
        self.p100_submenu.setChecked(True)
        self.zoom_group.setDisabled(True)
        self.zoom_group.triggered.connect(self.changeZoom)

        #registering file submenus
        self.file_menu.addAction(self.open_submenu)

        # registering bounding box submenus
        self.bounding_boxes.addAction(self.export_submenu)
        self.bounding_boxes.addAction(self.init_submenu)

        #registering zoom submenus
        self.zoom_menu.addActions(self.zoom_group.actions())

        #registering menus to menubar
        self.menubar.addAction(self.file_menu.menuAction())
        self.menubar.addAction(self.zoom_menu.menuAction())
        self.menubar.addAction(self.bounding_boxes.menuAction())

    def setTexts(self):
        self.setWindowTitle("FIBVID Analyser")

        #file menu
        self.file_menu.setTitle("File")

        self.open_submenu.setText("Open")

        self.bounding_boxes.setTitle("Boxes")

        # bouding boxes menu
        self.export_submenu.setText("Export as Images")
        self.init_submenu.setText("Initialize with Model")

        #zoom menu
        self.zoom_menu.setTitle("Zoom")

        self.p50_submenu.setText("50%")
        self.p100_submenu.setText("100%")
        self.p100_submenu.setText("100%")
        self.p150_submenu.setText("150%")
        self.p200_submenu.setText( "200%")

    def selectFile(self):

        # get the file browser pop-up
        path, _ = QFileDialog.getOpenFileName(
            self.statusbar, 'Select Video File', '/home')
        self.vid_path = path
        self.initVideo()

    def exportImages(self):

        cursor_pos = self.vid.get(cv2.CAP_PROP_POS_FRAMES)

        markers = self.collection.find({})
        markers.batch_size(1000000000)

        markers = [marker for marker in markers]

        height, width = self.current_frame.shape[0:2]

        empty = np.zeros((height, width, 3), np.uint8)

        center = (int(width/2), int(height/2))

        i = 0

        last = 0

        for marker in markers:

            progress = int(i * 100 / len(markers))

            img = empty.copy()
            cv2.circle(img, center, 100, (255, 255, 255))
            cv2.circle(img, center, progress, (255, 255, 255), -1)

            print(progress)

            self.setFrame(img)
            cv2.waitKey(1)
            last = progress

            box = [marker["start_pos"], marker["end_pos"]]

            rbox = RBox.fromPointBoundingBox(box)

            self.vid.set(cv2.CAP_PROP_POS_FRAMES, marker["frame_no"] - 1)

            rtt, frame = self.vid.read()

            patch = rbox.extractPatchFromImage(frame, square=True)

            name = str(marker["_id"])
            name = "./exports/" + name + ".png"
            cv2.imwrite(name, patch)
            i += 1

        self.initVideo()

    def showProgress(self, progress, fps):

        height, width = self.current_frame.shape[0:2]

        empty = np.zeros((height, width, 3), np.uint8)

        center = (int(width / 2), int(height / 2))

        cv2.circle(empty, center, progress, (255, 255, 255), -1)
        empty[center[1] - 100: center[1] + 100, center[0] - 100: center[0] + 100] = cv2.bitwise_and(
            empty[center[1] - 100: center[1] + 100, center[0] - 100: center[0] + 100],
            empty[center[1] - 100: center[1] + 100, center[0] - 100: center[0] + 100], mask=self.coin)

        cv2.circle(empty, center, 98, (255, 255, 255))

        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(empty, "FPS: {}".format(fps), (10, 20), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

        self.setFrame(empty)

    def initializeWithAlgorithm(self):

        self.initVideo()
        self.analyser = RuntimeABGSC(vid_path=self.vid_path)

        # read progress image
        coin = cv2.imread("fish_coin_inv.png")
        self.coin = np.uint8(cv2.cvtColor(coin, cv2.COLOR_RGB2GRAY) > 150) * 255

        # empty collection
        self.collection.delete_many({})

        # frame cout
        frame_count = self.vid.get(cv2.CAP_PROP_FRAME_COUNT)
        counter = 0

        # disable scroll bar
        self.slider.setDisabled(True)

        # disable video
        self.vid = False

        markers = []

        while(self.analyser.status):

            # while video is not complete
            start = time()
            self.analyser.process(show_output=False)
            end = time()
            # increment counter
            counter += 1

            # calculate fps
            fps = int(1/(end - start))

            # show progress in display window
            progress = int(counter * 100 / frame_count)
            self.showProgress(progress, fps)

            for box in self.analyser.final_boxes:

                start_pos = (int(box[0][0]), int(box[0][1]))
                end_pos = (int(box[1][0]), int(box[1][1]))

                # add resultant marker to markers of current frame
                marker = Marker(start_pos, end_pos,
                                counter, CONFIGURED_CLASSES[3])
                markers.append(marker.toDictionary())
                #self.frame_panel.markers.append(marker)

        # add markers to database
        self.collection.insert_many(markers)

        self.initVideo()

    def changeZoom(self):

        # get selected option's value
        zoom = self.zoom_group.checkedAction().val

        # reset frame according to new scaling
        self.resetFrame(zoom)

    def resetFrame(self, zoom):

        self.zoom = zoom
        self.frame_panel.zoom = zoom

        #resize frame panel
        self.frame_panel.resize(self.vid_height * zoom, self.vid_width * zoom)

        #resize window if dynamic scaling is enabled
        if DYNAMIC_WINDOW_SCALING:
            self.resize(self.vid_height * zoom + FRAME_MARGIN_LEFT +
                        FRAME_MARGIN_RIGHT, self.vid_width * zoom +
                        FRAME_MARGIN_TOP + FRAME_MARGIN_BOTTOM)

            # reposition slider
            self.slider.move(SLIDER_MARGINS, self.vid_width * zoom - (SLIDER_HEIGHT +
                        SLIDER_MARGINS))

            # resize slider
            self.slider.resize(self.width() - SLIDER_MARGINS * 2, SLIDER_HEIGHT)

            # reposition frame lable
            self.statusbar.frame_lable.move(self.width() - 100, self.height() - 37)

        self.currentFrame()

    def initVideo(self):

        # reset zoom
        self.zoom = 1.0

        self.vid = cv2.VideoCapture()
        # load selected video
        rtt = self.vid.open(self.vid_path)

        # clear slider
        self.slider.disconnect()

        # seek slider to start
        self.slider.setValue(0)
        self.slider.valueChanged.connect(self.moveSliderToClickedPosition)

        if rtt == False:
            if self.vid_path == "":
                self.statusbar.setStatusTip("No file selected")
            else:
                self.statusbar.setStatusTip("Error: Format not supported")

            # disalbe zoom options
            self.zoom_group.setDisabled(True)

            # clean video from memory
            self.vid = False

            # disable slider
            self.slider.setDisabled(True)

            return
        else:
            self.statusbar.setStatusTip("Ready")

            # set collection
            self.collection = self.db[self.vid_path]

        # seek to start
        self.vid.set(cv2.CAP_PROP_POS_FRAMES, 0)

        # read first frame
        rtt, frame = self.vid.read()

        # extract height and width of video
        self.vid_width, self.vid_height, self.vid_depth = np.shape(frame)
        self.vid_width *= self.zoom
        self.vid_height *= self.zoom

        self.current_frame = frame.copy()

        # resize frame view according to the video's geometery
        self.frame_panel.resize(self.vid_height, self.vid_width)

        # getting current frame number
        self.frame_no = self.vid.get(cv2.CAP_PROP_POS_FRAMES)

        # adding frame no to status tip
        self.statusbar.frame_lable.setText("Frame: {0}".format("%05.0i" % int(self.frame_no)))

        # reset frame to start
        self.resetFrame(self.zoom)

        #enable zoom options
        self.zoom_group.setDisabled(False)

        #enable slider
        self.slider.setDisabled(False)

        # enable algorithmBasedInitialization
        self.init_submenu.setDisabled(False)
        self.export_submenu.setDisabled(False)

        # plot the current frame on canvas
        self.frame_panel.content = frame.copy()
        self.setImageFrame(frame)

        # seek slider to start
        self.moveSliderToPosition(0)

    def setImageFrame(self, frame):

        # load image with markers
        self.frame_panel.loadMarkers()
        self.frame_panel.reDraw()
        self.frame_panel.dragStatus = "Ended"

    def setFrame(self, frame):
        # convert raw frame to QPixmap and set it on frame_panel
        frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        self.frame_panel.setPixmap(
            QPixmap.fromImage(
                QImage(frame, self.vid_height * self.zoom,
                       self.vid_width * self.zoom,
                       self.vid_height * self.zoom * self.vid_depth, QImage.Format_RGB888)))

    def nextFrame(self):
        # read next frame of video as Image
        rtt, frame = self.vid.read()

        if rtt:

            self.frame_panel.content = frame.copy()
            self.current_frame = frame.copy()

            # check if there is a next frame and convert cv Image to Pixmap
            frame = cv2.resize(frame, None, fx = self.zoom, fy = self.zoom,
                               interpolation = cv2.INTER_CUBIC)

            # initializing markers on frame_panel
            self.frame_panel.markers = []

            # getting current frame number
            self.frame_no = self.vid.get(cv2.CAP_PROP_POS_FRAMES)

            # clear slider
            self.slider.disconnect()

            # seek slider to start
            self.slider.setValue(self.frame_no * 100/self.vid.get(cv2.CAP_PROP_FRAME_COUNT))
            self.slider.valueChanged.connect(self.moveSliderToClickedPosition)

            self.setImageFrame(frame)

            #adding frame no to status tip
            self.statusbar.frame_lable.setText("Frame: {0}".format( "%05.0i" % int(self.frame_no)))

    def previousFrame(self):
        # set current frame number to 2 frames backward
        self.vid.set(cv2.CAP_PROP_POS_FRAMES,
                     self.vid.get(cv2.CAP_PROP_POS_FRAMES) - 2)
        # get next frame
        self.nextFrame()

    def currentFrame(self):

        self.frame_panel.content = self.current_frame.copy()

        # check if there is a next frame and convert cv Image to Pixmap
        frame = cv2.resize(self.current_frame.copy(), None, fx=self.zoom, fy=self.zoom,
                           interpolation=cv2.INTER_CUBIC)
        self.setImageFrame(frame)

    def keyPressEvent(self, event):

        # don't do anything if no video is selected
        if self.vid == False:
            return

        # Key press event on window
        if type(event) == QKeyEvent and event.key() == Qt.Key_D:

            # navigate forward if D pressed
            self.nextFrame()
        if type(event) == QKeyEvent and event.key() == Qt.Key_A:

            # navigate backward if A pressed
            self.previousFrame()

        if type(event) == QKeyEvent and event.key() == Qt.Key_Plus:

            # zoom in
            self.resetFrame(self.zoom + 1)

        if type(event) == QKeyEvent and event.key() == Qt.Key_Minus:

            # zoom out if zoom factor is greater than 1
            if(self.zoom > 1.0):
                self.resetFrame(self.zoom - 1)

    def moveSliderToClickedPosition(self):

        # enable slider to move with mouse click

        # get click position relative to slider
        click_position = self.slider.mapFromGlobal(QCursor.pos()).x()
        self.moveSliderToPosition(click_position)

    def moveSliderToPosition(self, position):

        # set position of slider to position by setting its value
        slider_completion_ratio = position / self.slider.width()
        self.slider.setValue(slider_completion_ratio * 100)

        # seek video accordingly
        if self.vid:
            self.vid.set(cv2.CAP_PROP_POS_FRAMES,
                         self.vid.get(cv2.CAP_PROP_FRAME_COUNT) * slider_completion_ratio)

            # refresh frame
            self.nextFrame()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())

