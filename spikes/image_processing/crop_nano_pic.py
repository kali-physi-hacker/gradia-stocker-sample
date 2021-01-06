import os
from datetime import datetime

import numpy as np
from matplotlib import pyplot as plt
from skimage.color import rgb2gray
from skimage.feature import canny
from skimage.filters import threshold_local
from skimage.io import imread  # , imsave
from skimage.measure import label, regionprops
from skimage.morphology import binary_closing, disk
from skimage.transform import resize

# camera is 1600x1200
NANO_PHOTO_WIDTH = 1600
# we resize to much smaller (1/8) because we want to process faster
MULTIPLE = 8
SMALL_SIZE = NANO_PHOTO_WIDTH / 8


RED = (0.8, 0.1, 0.1)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0.1, 0.1, 0.8)


def pad_into_square(img, gray_scale=False):
    longer_side = max(img.shape)
    # assert img.shape[0] == NANO_PHOTO_WIDTH, f"wrong shape {img.shape}"

    pad_bottom = longer_side - img.shape[0]
    pad_right = longer_side - img.shape[1]

    if gray_scale:
        return np.pad(img, [(0, pad_bottom), (0, pad_right)], "constant")
    else:
        return np.pad(img, [(0, pad_bottom), (0, pad_right), (0, 0)], "constant")


def minify(img, gray_scale=False):
    print(datetime.utcnow(), "resizing image")
    if gray_scale:
        return resize(img, (SMALL_SIZE, SMALL_SIZE), anti_aliasing=False, mode="edge")
    else:
        return rgb2gray(resize(img, (SMALL_SIZE, SMALL_SIZE), anti_aliasing=True, mode="edge"))


def get_area_of_interest(gray_scale_img):
    assert gray_scale_img.any()
    print(datetime.utcnow(), "getting areas of interest")

    # threshold to black and white
    local_thresh = threshold_local(gray_scale_img, block_size=151)
    thresholded = gray_scale_img > local_thresh

    # find edges from thresholded images-- gives a binary b or w image
    edges = canny(thresholded, sigma=1)

    # fill in small black spots
    # use a slightly larger neighborhood than default to make it even less spotty
    closed = binary_closing(edges, selem=disk(2))

    # find the largest region
    region_labels = label(closed, connectivity=1)
    biggest_region = max(regionprops(region_labels), key=lambda region: region.area)
    min_row, min_col, max_row, max_col = biggest_region.bbox
    print(biggest_region.bbox)

    width = max_col - min_col
    height = max_row - min_row

    length = max([width, height])

    extra_width = int((length - width) / 2 + length / 8)
    extra_height = int((length - height) / 2 + length / 8)

    return (
        max(min_row - extra_height, 0),
        max(min_col - extra_width, 0),
        min(max_row + extra_height, SMALL_SIZE),
        min(max_col + extra_width, SMALL_SIZE),
    )


def explain_work(before_target_after_images):
    nrows = len(before_target_after_images)
    images = [img for row in before_target_after_images for img in row]

    fig, axes = plt.subplots(nrows=nrows, ncols=3, figsize=(15, 11), sharex=True, sharey=True)

    plt.tight_layout()
    axes_list = axes.ravel()
    axes_list[0].set_title("Before", fontsize=30)
    axes_list[1].set_title("Identified Target", fontsize=30)
    axes_list[2].set_title("After", fontsize=30)

    for ii, ax in enumerate(axes_list):
        ax.axis("off")
        ax.imshow(images[ii], cmap=plt.cm.gray)
    plt.savefig("explanations.jpg")


explanations = []
for subdir, dirs, files in os.walk("nano"):
    for file_name in files:
        print(datetime.utcnow(), "processing", file_name)

        original = pad_into_square(imread(os.path.join("nano", file_name)))
        small_gray_img = minify(original)

        small_coordinates = get_area_of_interest(small_gray_img)
        print(small_coordinates)

        min_row, min_col, max_row, max_col = (coord * MULTIPLE for coord in small_coordinates)

        transformed = minify(pad_into_square(original[min_row:max_row, min_col:max_col]))

        explanations.append([small_gray_img, transformed, transformed])

explain_work(explanations)
