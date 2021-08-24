from collections import namedtuple
from datetime import datetime
from math import cos, sin

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy import ndimage as ndi
from skimage.color import rgb2gray
from skimage.draw import disk, line_aa
from skimage.feature import canny
from skimage.io import imread
from skimage.transform import (
    hough_circle,
    hough_circle_peaks,
    hough_line,
    hough_line_peaks,
    probabilistic_hough_line,
    resize,
    rotate,
)

RED = (0.8, 0.1, 0.1)
BLACK = (0, 0, 0)
BLUE = (0.1, 0.1, 0.8)

Pixel = namedtuple("Pixel", ["row", "col"])


def generate_exposure_histogram(image):
    plt.figure()
    plt.title("Exposure Histogram")
    plt.xlabel("exposure")
    plt.ylabel("# of pixels")

    plt.hist(rgb2gray(img).ravel() * 255, color="gray", histtype="stepfilled", bins=256, alpha=0.3)
    plt.hist(img[:, :, 0].ravel(), color="red", histtype="step", bins=256)
    plt.hist(img[:, :, 1].ravel(), color="green", histtype="step", bins=256)
    plt.hist(img[:, :, 2].ravel(), color="blue", histtype="step", bins=256)
    plt.legend(["Gray Scale", "Red", "Green", "Blue"])

    plt.savefig("exposure histogram.png")


def find_stone(img):
    # for a better version, see https://scikit-image.org/docs/stable/user_guide/tutorial_segmentation.html
    # find the edges; returns a 2d bool array, True for edge
    edges = canny(rgb2gray(img) * 255, sigma=25)

    # fill holes of edges that make a loop
    filled = ndi.binary_fill_holes(edges)
    # label: background is zero and each cluster is a diff number
    labelled_array, num_features = ndi.label(filled)
    assert num_features > 1, "ohoh, couldn't find any edges"
    # count the number of pixels for each cluster
    label_count = np.bincount(labelled_array.ravel())
    # mask that only true for large clusters
    cluster_to_mask_mapping = label_count > 200
    # set the background cluster also False
    cluster_to_mask_mapping[0] = False

    # a 2d array that is True inside the stone circle
    cleaned = cluster_to_mask_mapping[labelled_array]

    return cleaned


def find_perfect_circle(gray_scale_img):
    assert gray_scale_img.any()
    # https://scikit-image.org/docs/dev/auto_examples/edges/plot_circular_elliptical_hough_transform.html
    edges = canny(gray_scale_img, sigma=1)

    # apply hough transform to fit edge into a perfect circle
    hough_radii = np.arange(112, 512, 10)
    hough_spaces = hough_circle(edges, hough_radii)
    accums, center_xs, center_ys, radii = hough_circle_peaks(hough_spaces, hough_radii, total_num_peaks=1)
    yield (center_xs[0], center_ys[0])
    # make the circle radius slightly larger in case of imperfect stones
    yield radii[0] + 15
    for radius_adj in [-10, 10]:
        rows, cols = disk((center_xs[0], center_ys[0]), radii[0] + radius_adj)
        mask = np.zeros_like(gray_scale_img, dtype=bool)
        try:
            mask[cols, rows] = True
        except IndexError:
            # when x or y is outside of boundary
            pass
        yield mask


def find_square(gray_scale_img, ignore_area):
    assert gray_scale_img.any()
    edges = canny(gray_scale_img, sigma=1)
    edges[ignore_area] = False

    tested_angles = np.linspace(0, np.pi, 361)
    hough_spaces, angles, distances = hough_line(edges, theta=tested_angles)

    mask = np.zeros_like(gray_scale_img, dtype=bool)
    assert gray_scale_img.shape[0] == gray_scale_img.shape[1]
    max_position = gray_scale_img.shape[0] - 1

    accums, angles, distances = hough_line_peaks(
        hough_spaces, angles, distances, num_peaks=8, min_distance=50, min_angle=15
    )
    # find parallel lines and save the line in the middle parallel to them
    lines = sorted(zip(angles, distances))
    print(f"found {len(lines)} lines")
    center_lines = []

    for ii, (angle1, dist1) in enumerate(lines):
        for angle2, dist2 in lines[ii + 1 :]:
            score = abs(angle1 - angle2)
            if score < 0.20:
                center_lines.append([score, (angle1 + angle2) / 2, (dist1 + dist2) / 2])
    print(f"found {len(center_lines)} pairs of parallel lines")
    (_, a0, d0), (_, a1, d1) = sorted(center_lines)[0:2]

    center_x = (d0 * sin(a1) - d1 * sin(a0)) / sin(a1 - a0)
    center_y = (d0 - center_x * cos(a0)) / sin(a0)

    assert abs(center_y - (d1 - center_x * cos(a1)) / sin(a1)) < 1

    # find the intersect of the two most parallel lines
    # generate mask for explainability/illustrative purposes
    for angle, dist in zip(angles, distances):
        if abs(angle - a0) > 0.05 and abs(angle - a1) > 0.05:
            continue
        if angle == 0:
            xs = [dist, dist]
            ys = [0, max_position]
        elif angle == np.pi / 2:
            xs = [0, max_position]
            ys = [dist, dist]
        else:
            xs = [0, max_position]
            ys = [(dist - x * cos(angle)) / sin(angle) for x in xs]
            ys.extend([0, max_position])
            xs.extend([(dist - y * sin(angle)) / cos(angle) for y in ys[2:4]])

            df = pd.DataFrame({"x": xs.copy(), "y": ys.copy()}).round(0)
            filtered = (
                df[(df.x >= 0) & (df.x <= max_position) & (df.y >= 0) & (df.y <= max_position)]
                .astype(int)
                .drop_duplicates()
            )

            assert filtered.shape[0] <= 2, f"ohoh, df was\n{df}\nand filtered was\n{filtered}"

            if len(filtered) < 2:
                # the line could just be outside the square
                print("skipping... angle", angle, "dist", dist)
                print(df)
                print(filtered)
                continue

        line_xs, line_ys, _ = line_aa(filtered.iloc[0].y, filtered.iloc[0].x, filtered.iloc[1].y, filtered.iloc[1].x)

        mask[line_xs, line_ys] = True
    return (center_x, center_y), a0, mask


def find_square_probabilisitc(gray_scale_img, ignore_area):
    edges = canny(gray_scale_img, sigma=1)
    edges[ignore_area] = False

    mask = np.zeros_like(gray_scale_img, dtype=bool)

    for pt1, pt2 in probabilistic_hough_line(edges, threshold=50, line_length=300, line_gap=20):
        xs, ys, _ = line_aa(pt1[1], pt2[1], pt1[0], pt2[0])

        mask[xs, ys] = True
    return mask


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
    plt.savefig("test.png")


original = imread("IMG_4503.png")


longer_side = max(original.shape)
pad_bottom = longer_side - original.shape[0]
pad_right = longer_side - original.shape[1]
original = np.pad(original, [(0, pad_bottom), (0, pad_right), (0, 0)], "constant")


print(datetime.utcnow(), "resizing image")
img = resize(original, (1024, 1024), anti_aliasing=True, mode="edge")
print(datetime.utcnow(), "done")
# generate_exposure_histogram(img)

explanations = []

original = img.copy()
center, radius, small_circle_mask, large_circle_mask = list(find_perfect_circle(rgb2gray(original)))
targetted = original.copy()
targetted[~large_circle_mask] = RED
transformed = original.copy()
transformed[~large_circle_mask] = BLACK
# crop to just show the circle
transformed = transformed[
    max(center[1] - radius, 0) : center[1] + radius, max(center[0] - radius, 0) : center[0] + radius
]
transformed = resize(transformed, (1024, 1024), anti_aliasing=True, mode="edge")
explanations.append([original, targetted, transformed])

original = transformed.copy()
center, angle, square_mask = find_square(rgb2gray(original), ignore_area=~large_circle_mask)
print(center, angle / np.pi * 180)
targetted = original.copy()
targetted[square_mask] = RED
transformed = original.copy()
transformed = rotate(transformed, (angle / np.pi * 180) % 90)
explanations.append([original, targetted, transformed])

original = transformed.copy()
center, angle, square_mask = find_square(rgb2gray(original), ignore_area=~large_circle_mask)
print(center, angle / np.pi * 180)
targetted = original.copy()
targetted[square_mask] = RED
transformed = original.copy()
transformed = rotate(transformed, (angle / np.pi * 180) % 90)
explanations.append([original, targetted, transformed])


explain_work(explanations)


# https://scikit-image.org/docs/dev/user_guide/transforming_image_data.html

# check there is only one cluster left
# center the stone
# need to make sure the cleaned is round/edge not cut off
