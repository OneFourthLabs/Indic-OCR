import os
import cv2
import numpy as np
from nms import nms

from indic_ocr.detection import Detector_Base

class EAST_Detector(Detector_Base):
    '''
    OpenCV's DNN-based EAST Inference
    Inspiration: https://bitbucket.org/tomhoag/opencv-text-detection/
    '''
    def __init__(self, model_path=None, min_confidence=0.5, nms_threshold=0.4):
        
        if not model_path:
            model_path = 'models/east/frozen_east_text_detection.pb'
            if not os.path.isfile(model_path):
                print('Downloading EAST OpenCV checkpoint to:', model_path)
                os.makedirs(os.path.dirname(model_path), exist_ok=True)
                east_pb_url = 'https://bitbucket.org/tomhoag/opencv-text-detection/raw/master/opencv_text_detection/frozen_east_text_detection.pb'
                import urllib.request
                urllib.request.urlretrieve(east_pb_url, model_path)
        
        self.net = cv2.dnn.readNet(model_path)
        
        self.layer_names = [
            "feature_fusion/Conv_7/Sigmoid",
            "feature_fusion/concat_3"]
        self.mean = (123.68, 116.78, 103.94)
        self.min_confidence = min_confidence
        self.nms_threshold = nms_threshold
    
    def pad_img(self, img, multiple_of=32):
        h, w = img.shape[:2]
        dw = 0
        if w % multiple_of:
            dw = multiple_of - w%multiple_of
        dh = 0
        if h % multiple_of:
            dh = multiple_of - h%multiple_of
        
        # return cv2.resize(img, (w+dw, h+dh))
        top, bottom = dh//2, dh-(dh//2)
        left, right = dw//2, dw-(dw//2)
        
        return cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=[0,0,0])
    
    def load_img(self, img_path):
        # RGB Image
        return self.pad_img(super().load_img(img_path))
    
    def detect(self, img):
        blob = cv2.dnn.blobFromImage(img, 1.0, (img.shape[1], img.shape[0]), self.mean, swapRB=False, crop=False)
        self.net.setInput(blob)
        (scores, geometry) = self.net.forward(self.layer_names)
        polygons = self.get_polygons(scores, geometry)
        return [{
            'type': 'text',
            'points': points
        } for points in polygons.tolist()]
    
    def get_polygons(self, scores, geometry):
        (rects, confidences, baggage) = self.decode(scores, geometry, self.min_confidence)
        offsets = [b['offset'] for b in baggage]
        thetas = [b['angle'] for b in baggage]
        
        polygons = rects2polys(rects, thetas, offsets)
        indicies = nms.polygons(polygons, confidences, score_threshold=self.min_confidence,
                                 nms_threshold=self.nms_threshold)
        return np.array(polygons)[indicies]

    def decode(self, scores, geometry, confidenceThreshold):
        
        # grab the number of rows and columns from the scores volume, then
        # initialize our set of bounding box rectangles and corresponding confidence scores
        (numRows, numCols) = scores.shape[2:4]
        confidences = []    
        rects = [] #(x,y,w,h)
        baggage =[]

        # loop over the number of rows
        for y in range(0, numRows):
            # extract the scores (probabilities), followed by the geometrical
            # data used to derive potential bounding box coordinates that
            # surround text
            scoresData = scores[0, 0, y]
            dTop =          geometry[0, 0, y]
            dRight =        geometry[0, 1, y]
            dBottom =       geometry[0, 2, y]
            dLeft =         geometry[0, 3, y]
            anglesData =    geometry[0, 4, y]
                
            # loop over the number of columns
            for x in range(0, numCols):
            
                # if our score does not have sufficient probability, ignore it
                if scoresData[x] < confidenceThreshold:
                    continue
        
                confidences.append(float(scoresData[x]))
        
                # compute the offset factor as our resulting feature maps will
                # be 4x smaller than the input image
                (offsetX, offsetY) = (x * 4.0, y * 4.0)
                    
                # extract the rotation angle for the prediction and then
                angle = anglesData[x]
                                            
                # offsetX|Y is where the dTop, dRight, dBottom and dLeft are measured from
                # calc the rect corners
                upperRight = (offsetX + dRight[x], offsetY - dTop[x])
                lowerRight = (offsetX + dRight[x], offsetY + dBottom[x])
                upperLeft = (offsetX - dLeft[x], offsetY - dTop[x])
                lowerLeft = (offsetX - dLeft[x], offsetY + dBottom[x])

                rects.append([
                    int(upperLeft[0]), # x
                    int(upperLeft[1]),  # y
                    int(lowerRight[0]-upperLeft[0]), # w
                    int(lowerRight[1]-upperLeft[1]) # h
                ])
                
                baggage.append({
                    "offset": (offsetX, offsetY),
                    "angle": anglesData[x],
                    "upperRight": upperRight,
                    "lowerRight": lowerRight,
                    "upperLeft": upperLeft,
                    "lowerLeft": lowerLeft,
                    "dTop": dTop[x],
                    "dRight": dRight[x],
                    "dBottom": dBottom[x],
                    "dLeft": dLeft[x]
                })
        
        return (rects, confidences, baggage)
    
## ---------- UTILITIES ---------- ##

import math

def rects2polys(rects, thetas, origins, ratioWidth=1, ratioHeight=1):
    """Convert rectangles (x,y, w, h) into polygons [(x0,y0), (x1, y1), (x2, y2), (x3, y3])

    :param rects: a list of rectangles, each specified as (x, y, w, h)
    :type rects: tuple
    :param thetas: the angle of rotation for each rectangle in radians
    :type theta: list of float
    :param origin: the point to rotate each rectangle around
    :type origin: list of tuple
    :param ratioWidth: optional width scaling factor, default 1.0
    :type ratioWidth: float
    :param ratioHeight: optional height scaling factor, default 1.0
    :type ratioHeight: float
    :return: a list of polygons, each specified by its (x,y) verticies
    :rtype: list
    """
    polygons = []
    for i, box in enumerate(rects):
        upperLeftX = box[0]
        upperLeftY = box[1]
        lowerRightX = box[0] + box[2]
        lowerRightY = box[1] + box[3]

        # scale the bounding box coordinates based on the respective ratios
        upperLeftX = int(upperLeftX * ratioWidth)
        upperLeftY = int(upperLeftY * ratioHeight)
        lowerRightX = int(lowerRightX * ratioWidth)
        lowerRightY = int(lowerRightY * ratioHeight)

        # create an array of the rectangle's verticies
        points = [
            (upperLeftX, upperLeftY),
            (lowerRightX, upperLeftY),
            (lowerRightX, lowerRightY),
            (upperLeftX, lowerRightY)
        ]

        # the offset is the point at which the rectangle is rotated
        rotationPoint = (int(origins[i][0] * ratioWidth), int(origins[i][1] * ratioHeight))

        polygons.append(rotatePoints(points, thetas[i], rotationPoint))

    return polygons


def rotatePoints(points, theta, origin):
    """Rotate the list of points theta radians around origin

    :param points: list of points, each given as (x,y)
    :type points:  tuple
    :param theta: the angle to rotate the points in radians
    :type theta: float
    :param origin: the point about which the points are to be rotated
    :type origin: tuple
    :return: list of rotated points
    :rtype: list
    """
    rotated = []
    for xy in points:
        rotated.append(rotate_around_point(xy, theta, origin))

    return rotated


def rotate_around_point(xy, radians, origin=(0, 0)):
    """Rotate a point around a given point.

    Adapted from `LyleScott/rotate_2d_point.py` <https://gist.github.com/LyleScott/e36e08bfb23b1f87af68c9051f985302>`_

    :param xy: the (x,y) point to rotate
    :type xy: tuple
    :param radians: the angle in radians to rotate
    :type radians: float
    :param origin: the point to rotate around, defaults to (0,0)
    :returns: the rotated point
    """
    x, y = xy
    offset_x, offset_y = origin
    adjusted_x = (x - offset_x)
    adjusted_y = (y - offset_y)
    cos_rad = math.cos(radians)
    sin_rad = math.sin(radians)
    qx = offset_x + cos_rad * adjusted_x + sin_rad * adjusted_y
    qy = offset_y + -sin_rad * adjusted_x + cos_rad * adjusted_y

    return qx, qy
