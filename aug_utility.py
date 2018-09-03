import numpy as np
import cv2
from pixcel import *
from scipy import ndimage
import math
from socket import *
from config import *
from time import time


def find_bounding_boxes(fimage, lables):

    # initialize boxes array
    boxes = []

    for lable in lables:

        # iterate all lables

        # filter out image pixels with current lable
        labled = (fimage == lable) + 0

        # find indexes
        box = find_bounding_box(labled)

        # append found bouding box
        boxes.append(box)

    return boxes

def find_margined_bounding_boxes(fimage, lables, margins):

    # initialize boxes array
    boxes = []

    for lable in lables:

        # iterate all lables

        # filter out image pixels with current lable
        labled = (fimage == lable) + 0

        # find indexes
        box = find_bounding_box(labled, margins)

        # append found bouding box
        boxes.append(box)

    return boxes

def find_bounding_box(binary_matrix, margins=(0, 0)):

    # extract indexes of foreground pixels
    indicies = np.array(np.nonzero(binary_matrix + 0))

    # get contours
    ys = margins[1] + np.amin(indicies[0])
    ye = margins[1] + np.amax(indicies[0])

    xs = margins[0] + np.amin(indicies[1])
    xe = margins[0] + np.amax(indicies[1])

    # return contours
    return [(xs, ys), (xe, ye)]

def weightFilter(image, lables, weight):

    max = 0

    weights = np.zeros((lables))

    fimage = np.zeros_like(image)

    retained_lables = []

    for i in range(lables):
        weights[i] = np.sum(np.sum(image == i))

        if weights[i] > weights[max]:
            max = i

        if weights[i] > weight:
            fimage += np.uint8((image == i) + 0)
            retained_lables.append(i)

    fimage -= np.uint8((image == max) + 0)

    fimage = np.uint8(fimage * 255)

    boxes = []

    if (len(retained_lables) > 0):

        retained_lables.remove(max)
        boxes = find_bounding_boxes(image.copy(), retained_lables)

    return fimage, boxes


def weightFilterMini(image, weight):

    image = np.uint8(image)
    # extract contours
    image, contours, hierarchy = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    final_contours = []

    for cnt in contours:

        if cv2.contourArea(cnt) >= weight:

            # add it to final_contours
            final_contours.append(cnt)

    fimage = np.zeros((image.shape[:2]), np.uint8)
    cv2.drawContours(fimage, final_contours, -1, 255, -1)

    boxes = RBox.toPointBoundingBoxes(RBox.fromClassicalBoundingBoxes([cv2.boundingRect(cnt) for cnt in final_contours]))

    return fimage, boxes

def weightFilterMargined(image, lables, weight, margins):
    max = 0

    weights = np.zeros((lables))

    fimage = np.zeros_like(image)

    retained_lables = []

    for i in range(lables):

        weights[i] = np.sum(np.sum(image == i))

        if weights[i] > weights[max]:
            max = i

        if weights[i] > weight:
            fimage += np.uint8((image == i) + 0)
            retained_lables.append(i)

    fimage -= np.uint8(image == max)

    fimage = np.uint8(fimage * 255)

    boxes = []

    if (len(retained_lables) > 0):
        retained_lables.remove(max)
        boxes = find_margined_bounding_boxes(image.copy(), retained_lables, margins)

    return fimage, boxes

def calculatePossiblePadding(box, shape, default = 20):

    w_pad = default
    h_pad = default

    # dynamic padding
    if default == 0:

        rbox = RBox.fromPointBoundingBox(box)
        w_pad = round(0.205 * rbox.w)
        h_pad = round(0.205 * rbox.h)

    # extract with and height from shape
    height, width = shape[0:2]

    # extract starting, ending x and y from box
    ((x_start, y_start), (x_end, y_end)) = box

    # check if is it possible to add certain padding
    # if not add possible padding for all 4 points
    pad_x_start = h_pad
    if y_start - pad_x_start < 0:
        pad_x_start = y_start

    pad_y_start = w_pad
    if x_start - pad_y_start < 0:
        pad_y_start = x_start

    pad_x_end = w_pad
    if y_end + pad_x_end >= height:
        pad_x_end = height - y_end - 1

    pad_y_end = h_pad
    if x_end + pad_y_end >= width:
        pad_y_end = width - x_end - 1

    # return resultant padding
    return pad_x_start, pad_x_end, pad_y_start, pad_y_end


def findConnectedComponents(frame, threshold = 150, blur_radius = 1.0):

    img = frame.copy()  # gray-scale image

    # smooth the image (to remove small objects)
    imgf = ndimage.gaussian_filter(img, blur_radius)

    # find connected components
    labeled, nr_objects = ndimage.label(imgf > threshold)

    return labeled, nr_objects


def drawBoundingBox(im, start, end, color):
    cv2.rectangle(im, start, end, color, 1)

def pwpBasedTracking(image, frame_models, threshold):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    predicted = np.zeros((image.shape[0:2]), np.uint8)
    # FOREACH GIVEN  PATCH AND ITS MODEL, APPLY MODEL TO PATCH
    for fm in frame_models:

        patch = extractPatch(image, fm[1])
        #patch = cv2.medianBlur(patch, 5)
        mask = np.zeros(patch.shape[0:2], np.uint8)
        res = applyModel(patch, mask, fm[0])
        res = cv2.morphologyEx(res, cv2.MORPH_OPEN, kernel)
        res = cv2.morphologyEx(res, cv2.MORPH_CLOSE, kernel)
        res = cv2.morphologyEx(res, cv2.MORPH_OPEN, kernel)
        res = cv2.morphologyEx(res, cv2.MORPH_CLOSE, kernel)
        if(len(np.nonzero(res)[0]) > max(fm[2] * threshold, 10) ):
            predicted[fm[1][0]: fm[1][1], fm[1][2]: fm[1][3]] += res;

    return predicted

def extractPatch(im, box):

    # extract coordinates
    x1, x2, y1, y2 = box

    # extract and return patch
    return im[x1: x2, y1: y2, :]

def randomColor():

    return np.random.randint(0, 255, (1, 3))[0].tolist()

def performColorProcessing(image, mask, iterations = 1):

    # initialize kernel
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

    for i in range(iterations):
        model = computePosteriors(image, np.uint8(mask > 0) + 0)
        mask = applyModel(image, mask, model)

        cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel=kernel)

    return mask

def killDyingLables(frame, mask, threshold = 0.5):

    # get initial weights of lables
    initial_weights = np.array([np.sum(frame == lable) for lable in range(np.amax(frame) + 1)]) + 0.00001

    # get final labled frame
    labled_frame = frame * mask

    # get final weights
    final_weights = np.array([np.sum(labled_frame == lable) for lable in range(np.amax(frame) + 1)])

    # final probabilites
    final_probs = (final_weights/initial_weights) < threshold

    for lable in range(len(final_probs)):

        dying = final_probs[lable]

        # check is lable is dying
        if dying:

            # kill lable
            labled_frame -= np.uint8((labled_frame == lable) * lable)

    # return final labled frame
    return labled_frame

def killSmallLables(frame, threshold = 150):

    # get initial weights of lables
    initial_weights = np.array([np.sum(frame == lable) for lable in range(np.amax(frame) + 1)])

    # final probabilites
    final_probs = initial_weights < threshold

    for lable in range(len(final_probs)):

        dying = final_probs[lable]

        # check is lable is dying
        if dying:

            # kill lable
            frame -= np.uint8(np.uint8(frame == lable) * lable)

    # return final labled frame
    return frame

class RBox:

    def __init__(self):

        # initialize atributes
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0

    @staticmethod
    def fromClassicalBoundingBox(box):

        # initialize rbox
        rbox = RBox()

        # copy attributes
        rbox.x = box[0]
        rbox.y = box[1]
        rbox.w = box[2]
        rbox.h = box[3]

        # return rbox
        return rbox

    @staticmethod
    def fromClassicalBoundingBoxes(boxes):

        return [RBox.fromClassicalBoundingBox(box) for box in boxes]

    @staticmethod
    def fromRoughBoundingBox(box):

        # initialize rbox
        rbox = RBox()

        # copy attributes
        rbox.x = box[0]
        rbox.y = box[2]
        rbox.h = box[1] - box[0]
        rbox.w = box[3] - box[2]

        # return rbox
        return rbox

    @staticmethod
    def fromPointBoundingBox(box):

        # initialize rbox
        rbox = RBox()

        # copy attributes
        rbox.x = box[0][0]
        rbox.y = box[0][1]
        rbox.w = box[1][0] - box[0][0]
        rbox.h = box[1][1] - box[0][1]

        # return rbox
        return rbox

    @staticmethod
    def fromPointBoundingBoxes(boxes):

        return [RBox.fromPointBoundingBox(box) for box in boxes]

    def classicalBoundingBox(self):

        # return array like bounding box
        return [self.x, self.y, self.w, self.h]

    def pointBoundingBox(self):

        # return tuple of end points
        return ((self.x, self.y), (self.x + self.w, self.y + self.h))

    def area(self):

        return self.h * self.w

    def __or__(self, other_box):

        # initialize resultant box
        rbox = RBox()

        # calculate values
        rbox.x = min(self.x, other_box.x)
        rbox.y = min(self.y, other_box.y)
        rbox.w = max(self.x + self.w, other_box.x + other_box.w) - rbox.x
        rbox.h = max(self.y + self.h, other_box.y + other_box.h) - rbox.y

        return rbox

    def __and__(self, other_box):

        # initialize resultant box
        rbox = RBox()

        # calculate values
        rbox.x = max(self.x, other_box.x)
        rbox.y = max(self.y, other_box.y)
        rbox.w = min(self.x + self.w, other_box.x + other_box.w) - rbox.x
        rbox.h = min(self.y + self.h, other_box.y + other_box.h) - rbox.y

        if rbox.w < 0 or rbox.h < 0:

            # reinitailize or make it zero
            rbox = RBox()

        return rbox

    def similarity(self, other_box):

        # (A & B)/(A | B) = (A & B).area/(A.area + B.area - (A & B).area)
        #return (self & other_box).area()/(self.area() + other_box.area() - (self & other_box).area())
        min_area = min(self.area(), other_box.area())
        return (self & other_box).area()/min_area

    def __str__(self):

        return "{} {} {} {}".format(self.x, self.y, self.w, self.h)

    def __mul__(self, other_box):

        # calculate similarity and return
        return self.similarity(other_box)

    def __eq__(self, other):

        return self.x == other.x and self.y == other.y and self.w == other.w and self.h == other.h

    @staticmethod
    def similarityStats(boxes):

        # create matrix out of boxes
        sim_mat = np.array(boxes).reshape((-1, 1))
        sim_mat = np.tril(sim_mat.dot(sim_mat.T), -1)

        # return similarity matrix
        return sim_mat

    @staticmethod
    def similarityThreshold(boxes, threshold = 0.8):

        # get similarity matrix
        sim_mat = RBox.similarityStats(boxes)

        # find thresholded indexes
        ind = np.array(np.nonzero(sim_mat > threshold))

        # return in the form of list
        return list(ind.T)

    @staticmethod
    def reduceBoxes(boxes, threshold=0.8):

        similar_boxes = RBox.similarityThreshold(boxes, threshold)

        while len(similar_boxes) > 0:

            union = boxes[similar_boxes[0][1]] | boxes[similar_boxes[0][0]]

            # remove similar boxes
            del boxes[similar_boxes[0][0]]
            del boxes[similar_boxes[0][1]]

            boxes.append(union)

            similar_boxes = RBox.similarityThreshold(boxes, threshold)

        return boxes

    @staticmethod
    def toPointBoundingBoxes(boxes):

        return [box.pointBoundingBox() for box in boxes]

    @staticmethod
    def toClassicBoundingBoxes(boxes):

        return [box.classicalBoundingBox() for box in boxes]

    def extractPatchFromImage(self, image, square=False):

        # get bounding box end points
        (start, end) = self.pointBoundingBox()
        start, end = list(start), list(end)

        # check if square flag is on
        if square:

            im_h, im_w = image.shape[0:2]

            # adjust start and end so that height and width are equal
            if self.h != self.w:

                # find bigger size
                if self.h > self.w:

                    # find difference
                    diff = self.h - self.w

                    if start[0] >= int(diff/2):

                        start[0] -= math.floor(diff/2)
                        diff -=  math.floor(diff/2)
                    else:

                        diff -= start[0]
                        start[0] = 0

                    end[0] += diff

                    if end[0] >= im_w:

                        diff = end[0] - im_w + 1
                        end[1] -= diff
                else:

                    # find difference
                    diff = self.w - self.h

                    if start[1] >= int(diff / 2):

                        start[1] -= math.floor(diff / 2)
                        diff -= math.floor(diff / 2)
                    else:

                        diff -= start[1]
                        start[1] = 0

                    end[1] += diff

                    if end[1] >= im_h:
                        diff = end[1] - im_h + 1
                        end[0] -= diff

        # return patch
        return image[start[1]: end[1], start[0]: end[0]]

    def addPatchtoImage(self, image, patch):

        # get bounding box end points
        (start, end) = self.pointBoundingBox()

        # patch in to image
        image[start[1]: end[1], start[0]: end[0]] = patch

        # return image
        return image

def askForLable(patch):

    # write an image to send
    cv2.imwrite("patch.jpg", patch)

    # setup client socket
    clientSock = socket(AF_INET, SOCK_STREAM)
    clientSock.connect((TCP_IP, TCP_PORT))

    # open image
    image = open("patch.jpg", 'rb')

    # read bytes equal to buffer size
    data = image.read(BUFFER_SIZE)

    # while image still has data
    while (data):

        # send data to server
        clientSock.send(data)

        # read more data if available
        data = image.read(BUFFER_SIZE)

    # close file
    image.close()

    # signal server to end data stream
    clientSock.shutdown(SHUT_WR)

    # recieved lable as binary data from server and convert it to string
    label = clientSock.recv(1024)
    label = label.decode("utf-8")

    return label
