import cv2

from constants import RESULT_IMAGE_FOLDER

FILE_NAME = "info_images/volleyball.jpg"


def get_rotation(
    file_path=None,
    image_matrix=None,
    rotation_angle=0,
    show_image=False,
    result_file_name=None,
):
    if file_path:
        # Read image from disk.
        img = cv2.imread(file_path)
    elif image_matrix.any():
        img = image_matrix
    else:
        raise Exception("No image provided!!")
    # Shape of image in terms of pixels.
    (rows, cols) = img.shape[:2]

    # getRotationMatrix2D creates a matrix needed for transformation.
    # We want matrix for rotation w.r.t center to rotation_angle degree without scaling.
    rotated_matrix = cv2.getRotationMatrix2D(
        center=(cols / 2, rows / 2), angle=rotation_angle, scale=1
    )
    resultant_matrix = cv2.warpAffine(img, rotated_matrix, (cols, rows))
    # Write image back to disk.
    # timestamp = get_timestamp()
    cv2.imwrite(f"{RESULT_IMAGE_FOLDER}/{result_file_name}", resultant_matrix)
    if show_image:
        cv2.imshow("Resized image", resultant_matrix)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return resultant_matrix


if __name__ == "__main__":
    FILE_NAME = "info_images/volleyball.jpg"
    get_rotation(
        file_path=FILE_NAME, image_matrix=None, rotation_angle=45, show_image=True
    )
