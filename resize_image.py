import cv2


def get_resize(
    filename=None,
    image_matrix=None,
    height_change_factor=0.0,
    width_change_factor=0.0,
    show_image=False,
):
    if filename:
        print(f"filename_to_size={filename}")
        # Read image from disk.
        img = cv2.imread(filename)
        # cv2.imshow("Original Image", img)
    elif image_matrix:
        img = image_matrix
    else:
        raise Exception("No image provided!!")
    # Get number of pixel horizontally and vertically.
    (height, width) = img.shape[:2]

    # Specify the size of image along with interpolation methods.
    # cv2.INTER_AREA is used for shrinking, whereas cv2.INTER_CUBIC or #INTER_LINEAR (faster but still looks OK)
    # is used to enlarge an image.
    resized_image_matrix = cv2.resize(
        src=img,
        dsize=(
            int(width * (1 + width_change_factor)),
            int(height * (1 + height_change_factor)),
        ),
        interpolation=cv2.INTER_AREA,
    )
    # Write image back to disk.
    # timestamp = get_timestamp()
    # cv2.imwrite(f'{RESULT_IMAGE_FOLDER}/result_resize_{timestamp}.jpg', resized_image_matrix)
    if show_image:
        cv2.imshow("Resized image", resized_image_matrix)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return resized_image_matrix


if __name__ == "__main__":
    FILE_NAME = "info_images/volleyball.jpg"
    get_resize(
        filename=FILE_NAME,
        image_matrix=None,
        height_change_factor=-0.5,
        width_change_factor=-0.5,
        show_image=True,
    )
