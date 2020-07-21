import os
from glob import glob
from PIL import Image
import cv2
import numpy as np
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

degrees_to_cv2_rotation = {
    90 : cv2.ROTATE_90_CLOCKWISE,
    180: cv2.ROTATE_180,
    -90: cv2.ROTATE_90_COUNTERCLOCKWISE,
}

def crop_image_using_polygon(img, polygon):
    '''
    Returns a cropped region as a rectangle by warping the
    given points into a suitable 2D image.
    
    Useful for detectors that produce non-rectangular boxes.
    Read: jdhao.github.io/2019/02/23/crop_rotated_rectangle_opencv/#the-better-way
    '''
    # contour points
    cnt = np.array(polygon).reshape((-1, 1, 2))
    rect = cv2.minAreaRect(cnt)
    src_pts = np.int0(cv2.boxPoints(rect)).astype("float32")
    
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
    return cv2.rotate(warped, degrees_to_cv2_rotation[angle])
