import cv2
import numpy as np

from PyQt5.QtWidgets import (QLabel)
from PyQt5.QtCore import *
from PyQt5.QtGui import (QMouseEvent, QImage, QPixmap)

from config import *
from aug_utility import *
from bgs import *

class DLabel(QLabel):

    def __init__(self, caller, mainWindow):
        super().__init__(caller)
        self.setMouseTracking(True)
        self.dragStatus = "Ended"
        self.zoom = 1
        self.mainWindow = mainWindow
        self.markers = []
        self.last_hovered_marker = 0
        self.marker_color = DEFAULT_COLOR
        self.lables = CONFIGURED_CLASSES
        self.class_color = CLASS_COLOR_MAPPING
        self.backup_content = False

    def mousePressEvent(self, event):

        # check if event button is right click or no video selected
        if event.button() == Qt.RightButton or self.mainWindow.vid == False:

            if self.dragStatus == "Marker hovered":
                self.mainWindow.classes[self.markers[self.last_hovered_marker].lable].setChecked(True)
                self.contextMenuRequested(event.pos())
            return

        #reset drag position
        self.dragStartPos = (int(event.pos().x() / self.zoom),
                             int(event.pos().y() / self.zoom))
        self.dragEndPos = (int(event.pos().x() / self.zoom),
                           int(event.pos().y() / self.zoom))

        #set drag status to started
        self.dragStatus = "Started"

        # backup original image
        self.backup_content = self.content

        # set marker color to default class
        self.marker_color = self.class_color[CONFIGURED_CLASSES[0]]

    def deleteHoveredMarker(self):

        # remove marker from database
        self.mainWindow.collection.remove(self.markers[self.last_hovered_marker].toDictionary())

        del self.markers[self.last_hovered_marker]

    def changeHoveredMarker(self):

        # get hovered box
        hovered_box = [self.markers[self.last_hovered_marker].start_pos, self.markers[self.last_hovered_marker].end_pos]

        # extract patch from image
        patch = RBox.fromPointBoundingBox(hovered_box).extractPatchFromImage(self.mainWindow.current_frame)

        # ask for lable from classifier
        updated_lable = askForLable(patch)

        # update marker
        self.updateMarkerClass(updated_lable)


    def toggleMarkerClass(self):

        # get selected option
        selected_option = self.mainWindow.class_group.checkedAction().text()

        # update to new option
        self.updateMarkerClass(selected_option)

    def updateMarkerClass(self, lable):

        # update change in database
        self.mainWindow.collection.update_one(self.markers[self.last_hovered_marker].toDictionary(),
                                              {"$set": {"lable": lable}})

        # set marker class value to selected value
        self.markers[self.last_hovered_marker].lable = lable

        # show updated content
        self.backup_content = self.recreateWithMarkers()
        self.handleMarkers(self.dragEndPos)

    def loadMarkers(self):

        # read documents from database
        docs = self.mainWindow.collection.find({"frame_no": self.mainWindow.frame_no})
        self.markers = []

        for doc in docs:
            marker = Marker()
            self.markers.append(marker.fromDictionary(doc))

        # show updated content
        if len(self.markers) > 0:

            # keep a copy of original content
            self.original_content = self.content.copy()

            # draw markers
            self.content = self.recreateWithMarkers()

    def contextMenuRequested(self, point):

        # show context menu of main window
        self.mainWindow.context_menu.exec_(self.mapToGlobal(point))

    def deleteMarker(self):

        # delete last hovered marker
        self.deleteHoveredMarker()

        # show updated content
        self.backup_content = self.recreateWithMarkers()
        self.handleMarkers(self.dragEndPos)

    def getLable(self):

        # delete last hovered marker
        self.changeHoveredMarker()

        # show updated content
        self.backup_content = self.recreateWithMarkers()
        self.handleMarkers(self.dragEndPos)

    def mouseReleaseEvent(self, event):

        # check if event button is right click or drag status is still ended
        if event.button() == Qt.RightButton or self.dragStatus == "Ended":
            return

        #set drag ending position
        self.dragEndPos = (int(event.pos().x() / self.zoom),
                           int(event.pos().y() / self.zoom))

        #draw bounding box resultant of mouse events in default class color
        self.marker_color = self.class_color[CONFIGURED_CLASSES[0]]
        self.drawBoundingBox()

        # set drag status to started
        self.dragStatus = "Ended"

        # store original image
        if len(self.markers) == 0:
            self.original_content = self.backup_content.copy()

        # set resultant image in window object
        self.mainWindow.current_frame = self.content.copy()

        # add resultant marker to markers of current frame
        marker = Marker(self.dragStartPos, self.dragEndPos,
                                   self.mainWindow.frame_no, CONFIGURED_CLASSES[0])
        self.markers.append(marker)

        # add marker to database
        self.mainWindow.collection.insert_one(marker.toDictionary())

    def recreateWithMarkers(self):

        canvas = self.original_content.copy()

        # backup marker color
        backup_marker_color = self.marker_color

        for i in range(len(self.markers)):

            # set start and drag positions according to current marker
            self.dragStartPos = self.markers[i].start_pos
            self.dragEndPos = self.markers[i].end_pos
            self.marker_color = self.class_color[self.markers[i].lable]

            # draw bounding box
            canvas = self.drawBoundingBoxOnImage(canvas)

        # restore marker color
        self.marker_color = backup_marker_color

        return canvas

    def mouseMoveEvent(self, event):

        # update drag end position
        self.dragEndPos = (int(event.pos().x() / self.zoom),
                           int(event.pos().y() / self.zoom))

        if(self.dragStatus == "Started"):
            self.content = self.backup_content.copy()

            self.drawOverlayBox()
        else:

            # handle hovering over markers
            self.handleMarkers(self.dragEndPos)

    def handleMarkers(self, pos):

        backup_marker_color = self.marker_color

        for i in range(len(self.markers)):
            if (pos[0] >= self.markers[i].start_pos[0] and pos[0] <=
                self.markers[i].end_pos[0] and pos[1] >=
                self.markers[i].start_pos[1] and pos[1] <=
                self.markers[i].end_pos[1]):

                # show hover effect and return
                self.dragStartPos = self.markers[i].start_pos
                self.dragEndPos = self.markers[i].end_pos

                # backup unhovered image
                if self.dragStatus != "Marker hovered":
                    self.backup_content = self.content.copy()

                    # set drag status to marker hovered
                    self.dragStatus = "Marker hovered"
                    self.last_hovered_marker = i

                self.marker_color = self.class_color[self.markers[i].lable]
                self.drawOverlayBox()
                return

        self.marker_color = backup_marker_color

        # draw original image if hovering ends
        if self.dragStatus == "Marker hovered":

            self.content = self.backup_content
            self.reDraw()

            # set drag status to normal
            self.dragStatus = "Ended"

    def drawBoundingBox(self):

        self.content = self.backup_content.copy()

        cv2.rectangle(self.content, self.dragStartPos,
                      self.dragEndPos, self.marker_color, 1)

        self.reDraw()

    def drawBoundingBoxOnImage(self, image):

        cv2.rectangle(image, self.dragStartPos,
                      self.dragEndPos, self.marker_color, 1)

        return image

    def drawOverlayBox(self):
        cv2.rectangle(self.content, self.dragStartPos,
                      self.dragEndPos, self.marker_color, -1)

        buf = self.backup_content.copy()
        cv2.addWeighted(self.content, ALPHA, buf, 1 - ALPHA,
                        0, self.content)
        self.reDraw()

    def reDraw(self):

        temp = cv2.resize(self.content.copy(), None, fx=self.zoom, fy=self.zoom,
                           interpolation=cv2.INTER_CUBIC)

        self.mainWindow.setFrame(temp)

    '''def markerColorToggled(self):

        # get selected option
        selected_option = self.mainWindow.color_submenu.action_group.checkedAction().text()

        color_dictionary = {
            "Green": (0, 255, 0),
            "Red": (255, 0, 0),
            "Blue": (0, 0, 255)
        }

        # set marker color corresponding to selected option
        self.marker_color = color_dictionary[selected_option]

        # show updated content
        self.content = self.recreateWithMarkers()
        self.reDraw()'''

class Marker():

    def __init__(self, start_pos = (0, 0), end_pos = (0, 0), frame_no = 0, lable = False):

        # set start and end positions
        self.start_pos = start_pos
        self.end_pos = end_pos

        # set frame no.
        self.frame_no = frame_no

        # initailize lable
        self.lable = lable

        # sort start and end pos in ascending order
        self.sortCoordinates()

    def sortCoordinates(self):

        # create local copies
        x_set = self.start_pos[0]
        x_end = self.end_pos[0]

        y_set = self.start_pos[1]
        y_end = self.end_pos[1]

        # swap is necessary

        if x_set >= x_end:
            x_set = self.end_pos[0]
            x_end = self.start_pos[0]

        if y_set >= y_end:
            y_set = self.end_pos[1]
            y_end = self.start_pos[1]

        # reassign to class attributes
        self.start_pos = (x_set, y_set)
        self.end_pos = (x_end, y_end)

    def toDictionary(self):

        # convert python obj to raw python dictionary
        return {"start_pos": self.start_pos, "end_pos": self.end_pos, "frame_no": self.frame_no, "lable": self.lable}

    def fromDictionary(self, dict):

        # convert raw python dictionary to obj
        self.start_pos = (dict["start_pos"][0], dict["start_pos"][1])
        self.end_pos = (dict["end_pos"][0], dict["end_pos"][1])
        self.frame_no = dict["frame_no"]
        self.lable = dict["lable"]

        return self

    def __str__(self):
        return "Start: %s, End: %s, Frame_no: %f, Lable: %s" \
               % (self.start_pos, self.end_pos, self.frame_no, self.lable)