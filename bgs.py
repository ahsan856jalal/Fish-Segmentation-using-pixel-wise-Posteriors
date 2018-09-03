# IMPORT UTILITIES
import pybgs
from aug_utility import *
from time import time

LEFT_ARROW = 1113937
SPACEBAR = 1048608
ESC = 1048603
B = 1048674

class RuntimeABGSC:

    def __init__(self, vid_path, algorithm_params = {
        'algorithm': 'zivkovic_agmm', 'low': 10, 'high': 100,
        'alpha': 0.005, 'max_modes': 30
    }, bgs_weight_threshold = 50, posteriors_model_blob_padding = 20,
                 _frame_rate = 1, _post_processing = True, _color_processing = True ):

        # initialize instance varaiables
        self.algo_params = algorithm_params
        self.default_frame_rate = _frame_rate
        self.post_processing =  _post_processing
        self.vid_path = vid_path
        self.bgs_weight_threshold = bgs_weight_threshold
        self.posteriors_model_blob_padding = posteriors_model_blob_padding
        self.color_processing = _color_processing

        # initilize necessary objects
        self.initializeVideo()
        self.initializeBGS()

    def initializeVideo(self):

        # open video stream
        self.video = cv2.VideoCapture()
        self.video.open(self.vid_path)

        # get first frame from video
        self.status, self.frame = self.video.read()

        # initailize frame rate with default frame rate
        self.frame_rate = self.default_frame_rate

        # check if video is opened properly
        if self.status != True:

            # video didn't open correctly throw error
            raise ("Data Error", "Unable to open video!")
        else:

            # apply some preprocessing on frame
            self.frame = self.frameWisePreprocessing(self.frame)

    def initializeBGS(self):

        # initialize bgs model
        self.bgs_model = pybgs.BackgroundSubtraction()

        # initialize high, low threshold mask
        self.high_threshold_mask = np.zeros(shape=self.frame.shape[0:2], dtype=np.uint8)
        self.low_threshold_mask = np.zeros_like(self.high_threshold_mask)

        # initialize model with parameters
        self.bgs_model.init_model(self.frame, self.algo_params)
        self.bgs_model_interation_count = 0

    def frameWisePreprocessing(self, frame):

        frame = cv2.medianBlur(frame, 3)

        return frame

    def frameWisePostprocessing(self, frame):

        # initialize kernel
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

        # apply weight thresholding
        #(img, lables) = findConnectedComponents((frame > 200) * 255)
        #frame, boxes = weightFilter(img, lables, 150)

        frame, boxes = weightFilterMini((frame > 200) * 255, 50)

        # set final output boxes to final boxes attribute of object
        self.final_boxes = boxes

        # apply morphological operations
        frame = cv2.morphologyEx(frame, cv2.MORPH_OPEN, kernel)
        frame = cv2.dilate(frame, kernel, iterations=1)

        # return results
        return frame

    def patchWisePreprocessing(self, patch):

        # apply median blur
        patch = cv2.medianBlur(patch, 3)

        return patch

    def frameWiseColorProcessing(self, bounding_boxes, foreground):

        processed_foreground = np.zeros_like(foreground)

        for bounding_box in bounding_boxes:

            # calculate possible padding
            pad_x1, pad_x2, pad_y1, pad_y2 = calculatePossiblePadding(bounding_box, foreground.shape[0:2],
                                                                      self.posteriors_model_blob_padding)

            # extract starting, ending x and y from box
            ((x_start, y_start), (x_end, y_end)) = bounding_box

            # extract patch to apply processing on
            patch_bounds = [y_start - pad_x1, y_end + pad_x2, x_start - pad_y1, x_end + pad_y2]
            patch = extractPatch(self.frame, patch_bounds)

            # apply patch wise preprocessing
            patch = self.patchWisePreprocessing(patch)

            # prepare mask for patch
            mask = np.zeros(patch.shape[0:2], np.uint8)

            # extract mask width, height
            mask_height, mask_width = mask.shape[0:2]

            # extract mask's pixels from foreground
            mask[pad_x1: mask_height - pad_x2, pad_y1:mask_width - pad_y2] = foreground[y_start: y_end,
                                                                                  x_start: x_end]

            # apply pixcel wise posteriors
            model = computePosteriors(patch, np.uint8(mask == 255))
            resulting_patch = applyModel(patch, np.uint8(mask == 255), model)

            # update preocessed foreground with resulting patch
            processed_foreground[y_start - pad_x1: y_end + pad_x2, x_start - pad_y1: x_end + pad_y2] += resulting_patch

        return processed_foreground

    def applyPostBGSPreprocessing(self, frame):

        # preprocessing goes here

        return frame

    def startProcessing(self):

        # kickoff process
        while self.status:

            # move to the next frame
            self.process()

    def process(self, show_output=True):

        # apply bgs and update low, high threshold masks
        self.bgs_model.subtract(self.bgs_model_interation_count, self.frame,
                                self.low_threshold_mask, self.high_threshold_mask)
        self.bgs_model.update(self.bgs_model_interation_count, self.frame,
                              self.high_threshold_mask)

        # create copy of estimated foreground from algorithm
        foreground = self.low_threshold_mask.copy()

        foreground = self.applyPostBGSPreprocessing(foreground)

        # find connected components from foreground
        #(labled_foreground, lables) = findConnectedComponents((foreground > 200) * 255)

        # apply weighted filtering based on defined weight threshold
        #filtered_foreground, bounding_boxes = weightFilter(labled_foreground, lables, self.bgs_weight_threshold)

        filtered_foreground, bounding_boxes = weightFilterMini((foreground > 200) * 255, 10)

        self.bgs_resultant = filtered_foreground

        # apply color processing if color processing flag is on
        if self.color_processing:

            # apply post preocessing
            filtered_foreground = self.frameWiseColorProcessing(bounding_boxes, filtered_foreground)

        # apply post processing if post processing flag is on
        if self.post_processing:

            # apply post preocessing
            filtered_foreground = self.frameWisePostprocessing(filtered_foreground)

        # perform inverted intersection with frame
        self.output = self.invertedIntersection(self.frame.copy(), filtered_foreground)

        # display output
        if show_output:
            self.showOutput(self.output)
            self.showOutput(self.frame, "original")
            self.showOutput(self.bgs_resultant, "Segmented")

        # prepare next iteration
        self.prepareNextIteration()

        # check if video still has frames
        if (self.status != True and show_output):
            # show video end message
            print("Analysing finished")

    def prepareNextIteration(self):

        # increase iteration count
        self.bgs_model_interation_count += 1

        # detect if any key is pressed while analysing frame
        key = cv2.waitKey(self.frame_rate)

        # process key commands
        self.processKeyCommand(key)

        # load next frame
        status, self.frame = self.video.read()

        #update video status
        self.status = self.status and status

    def pauseResumeVideo(self):

        # toggle between pause and play
        if self.frame_rate == 0:
            self.frame_rate = self.default_frame_rate
        else:
            self.frame_rate = 0

    def previousFrame(self):

        # set video cursor to two frames back
        self.video.set(cv2.CAP_PROP_POS_FRAMES,
                self.video.get(cv2.CAP_PROP_POS_FRAMES) - 2)

    def stopAnalysis(self):

        # set status to false
        self.status = False

    def processKeyCommand(self, key):

        process = {
            SPACEBAR: self.pauseResumeVideo,
            LEFT_ARROW: self.previousFrame,
            ESC: self.stopAnalysis,
            B: self.saveSub
        }

        if key in process:
            process[key]()

    def saveSub(self):

        # write subtracted image to disk
        cv2.imwrite("bgs_im.png", self.bgs_resultant)

    def showOutput(self, output, win_name = "output"):

        # show cv2 image output
        cv2.imshow(win_name, output)

    def invertedIntersection(self, frame, foreground):

        # iterate all layers in image
        for layer in range(frame.shape[2]):

            # perform inverted intersection
            frame[:, :, layer] *= np.uint8(foreground/-255)

        # return results
        return frame

#runner = RuntimeABGSC(vid_path="10aa9067c36db50b6fa20c200718ec9a#201012101510.flv")
#runner = RuntimeABGSC(vid_path="Fish4k/camouflage1.flv")
#runner = RuntimeABGSC(vid_path="fish4.flv")
#runner.startProcessing()