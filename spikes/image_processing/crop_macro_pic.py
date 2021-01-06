import os
from datetime import datetime

import numpy as np
from skimage.color import rgb2gray
from skimage.draw import disk
from skimage.feature import canny
from skimage.io import imread, imsave
from skimage.transform import hough_circle, hough_circle_peaks, resize

# camera is 6744x4500
CANON_PHOTO_WIDTH = 6744
# we resize to much smaller (1/24) because we want to process faster
MULTIPLE = 24
SMALL_SIZE = 281


RED = (0.8, 0.1, 0.1)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0.1, 0.1, 0.8)


def pad_into_square(img):
    longer_side = CANON_PHOTO_WIDTH
    pad_bottom = longer_side - img.shape[0]
    pad_right = longer_side - img.shape[1]

    img = np.pad(img, [(0, pad_bottom), (0, pad_right), (0, 0)], "constant")

    # assert img.shape[0] == CANON_PHOTO_WIDTH, f"wrong shape {img.shape}"
    # assert img.shape[1] == CANON_PHOTO_WIDTH, f"wrong shape {img.shape}"
    return img


def minify(img):
    print(datetime.utcnow(), "resizing image")
    img = resize(img, (SMALL_SIZE, SMALL_SIZE), anti_aliasing=True, mode="edge")
    print(datetime.utcnow(), "done")
    return rgb2gray(img)


def find_perfect_circle(gray_scale_img):
    assert gray_scale_img.any()
    # https://scikit-image.org/docs/dev/auto_examples/edges/plot_circular_elliptical_hough_transform.html
    print(datetime.utcnow(), "finding edges")
    edges = canny(gray_scale_img, sigma=1)
    print(datetime.utcnow(), "done")

    # apply hough transform to fit edge into a perfect circle
    print(datetime.utcnow(), "computing hough spaces")
    hough_radii = np.arange(30, 140, 1)
    hough_spaces = hough_circle(edges, hough_radii)
    print(datetime.utcnow(), "done")
    print(datetime.utcnow(), "finding hough circle peaks")
    accums, center_xs, center_ys, radii = hough_circle_peaks(hough_spaces, hough_radii, total_num_peaks=1)
    print(datetime.utcnow(), "done")
    # make the circle radius slightly larger in case of imperfect stones
    return center_xs[0], center_ys[0], radii[0] + 2


def create_full_sized_mask(center_x, center_y, radii):
    shape = [CANON_PHOTO_WIDTH, CANON_PHOTO_WIDTH]
    mask = np.zeros(shape, dtype=bool)
    rows, cols = disk([center_x, center_y], radii, shape=shape)
    mask[cols, rows] = True
    return mask


for subdir, dirs, files in os.walk("stones"):
    for file_name in files:
        if file_name.endswith("_cropped.png"):
            continue
        print(datetime.utcnow(), "processing", file_name)

        original = pad_into_square(imread(os.path.join("stones", file_name)))

        small_img = minify(original)

        small_center_x, small_center_y, small_radii = find_perfect_circle(small_img)

        center_x = small_center_x * MULTIPLE
        center_y = small_center_y * MULTIPLE
        radii = small_radii * MULTIPLE

        full_sized_mask = create_full_sized_mask(center_x, center_y, radii)
        # make outside black
        original[~full_sized_mask] = BLACK

        # crop original full resolution pic to just show the circle
        img = original[max(center_y - radii, 0) : center_y + radii, max(center_x - radii, 0) : center_x + radii]

        # resize down to a standard web size
        img = resize(img, (1024, 1024), anti_aliasing=True, mode="edge")
        imsave(os.path.join("processed", file_name.split(".")[0] + "_photo.jpg"), img)
        # resize down to a standard web size
        img = resize(img, (3096, 3096), anti_aliasing=True, mode="edge")
        imsave(os.path.join("processed", file_name.split(".")[0] + "_macro.jpg"), img)
