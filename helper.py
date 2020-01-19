from datetime import datetime
from io import BytesIO

import cv2
import pytz
import requests
from skimage import io as skimage_io


def get_timestamp():
    est = pytz.timezone("US/Eastern")
    fmt = "%Y-%m-%dT%H:%M:%S"
    datestamp = datetime.now(tz=est).strftime(fmt)
    return datestamp


def read_image_for_oc2(resolved_url):
    # download the image using scikit-image
    image = skimage_io.imread(
        resolved_url
    )  # scikit-image represents images in RGB order
    image = cv2.cvtColor(
        image, cv2.COLOR_BGR2RGB
    )  # OpenCV represents images in BGR order so
    # convert the image from RGB to BGR
    cv2.imshow("Correct", image)
    cv2.waitKey(0)
    return image


def get_bytes_image_from_url(url):
    response = requests.get(url)
    binary_img = BytesIO(response.content)
    return binary_img
