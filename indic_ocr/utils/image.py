import os
from glob import glob
from PIL import Image
import cv2
import numpy as np
from scipy.spatial import distance as dist

IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg']

def get_all_images(folder):
    files = glob(os.path.join(folder, '*'))
    images = []
    for extension in IMAGE_EXTENSIONS:
        images += [file for file in files if file.lower().endswith(extension)]
    return images

def rgb2gray_uint8(rgb):
    if len(rgb.shape) == 2: return rgb
    return np.dot(rgb[...,:3], [0.2989, 0.5870, 0.1140]).astype(np.uint8)

def np2pil(np_img):
    return Image.fromarray(np_img)

def cv2pil(cv2_img):
    rgb = bgr2rgb(cv2_img)
    return Image.fromarray(rgb)

def reverse_channels(img):
    return img[..., ::-1]

def rgb2bgr(img):
    return reverse_channels(img)

def bgr2rgb(img):
    return reverse_channels(img)

def crop_image_using_quadrilateral(img, quadrilateral):
    '''
    Assume quadrilateral points in clockwise direction
    from top-left till bottom-left
    
    Useful for detectors that produce non-rectangular boxes.
    '''
    src_pts = np.int0(quadrilateral).astype("float32")
    w = int(max(
        cv2.norm(src_pts[1] - src_pts[0], cv2.NORM_L2),
        cv2.norm(src_pts[3] - src_pts[2], cv2.NORM_L2)
    ))
    h = int(max(
        cv2.norm(src_pts[3] - src_pts[0], cv2.NORM_L2),
        cv2.norm(src_pts[2] - src_pts[1], cv2.NORM_L2)
    ))
    
    dst_pts = np.array([
                    [0, 0],
                    [w-1, 0],
                    [w-1, h-1],
                    [0, h-1],
                    ], dtype="float32")
    
    return cv2.warpPerspective(img, cv2.getPerspectiveTransform(src_pts, dst_pts), (w, h))

degrees_to_cv2_rotation = {
    90 : cv2.ROTATE_90_CLOCKWISE,
    180: cv2.ROTATE_180,
    -90: cv2.ROTATE_90_COUNTERCLOCKWISE,
}

def crop_image_around_polygon(img, polygon):
    '''
    Returns a cropped region as a rectangle by warping the
    given contour points into a suitable 2D image.
    
    Read: jdhao.github.io/2019/02/23/crop_rotated_rectangle_opencv/#the-better-way
    '''
    # contour points
    cnt = np.array(polygon, dtype=np.int32).reshape((-1, 1, 2))
    rect = cv2.minAreaRect(cnt)
    src_pts = np.int0(cv2.boxPoints()).astype("float32")
    
    w, h = int(rect[1][0]), int(rect[1][1])
    dst_pts = np.array([
                    [0, h-1],
                    [0, 0],
                    [w-1, 0],
                    [w-1, h-1],
                    ], dtype="float32")
    warped = cv2.warpPerspective(img, cv2.getPerspectiveTransform(src_pts, dst_pts), (w, h))
    
    angle = int(rect[2])
    if not angle:
        return warped
    if angle not in degrees_to_cv2_rotation:
        # TODO: Fix bug. Currently returns as it is
        cv2.imshow('Bug with angle: ' + str(angle), warped)
        cv2.waitKey(0); cv2.destroyAllWindows()
        return warped
    return cv2.rotate(warped, degrees_to_cv2_rotation[angle])

def order_points_clockwise(pts):
    '''
    Src: pyimagesearch.com/2016/03/21/ordering-coordinates-clockwise-with-python-and-opencv/
    '''
    pts = np.array(pts)
    # sort the points based on their x-coordinates
    xSorted = pts[np.argsort(pts[:, 0]), :]
    # grab the left-most and right-most points from the sorted
    # x-roodinate points
    leftMost = xSorted[:2, :]
    rightMost = xSorted[2:, :]
    # now, sort the left-most coordinates according to their
    # y-coordinates so we can grab the top-left and bottom-left
    # points, respectively
    leftMost = leftMost[np.argsort(leftMost[:, 1]), :]
    (tl, bl) = leftMost
    # now that we have the top-left coordinate, use it as an
    # anchor to calculate the Euclidean distance between the
    # top-left and right-most points; by the Pythagorean
    # theorem, the point with the largest distance will be
    # our bottom-right point
    D = dist.cdist(tl[np.newaxis], rightMost, "euclidean")[0]
    (br, tr) = rightMost[np.argsort(D)[::-1], :]
    # return the coordinates in top-left, top-right,
    # bottom-right, and bottom-left order
    return [tl, tr, br, bl]
