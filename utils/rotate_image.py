import cv2
import exiftool

def rotate_image(img, img_name):
    try:
        with exiftool.ExifTool() as et:
            orientation = et.get_metadata(img_name)["EXIF:Orientation"]
    except KeyError:
        return None

    if orientation == 8:
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    if orientation == 6:
        img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    if orientation == 3:
        img = cv2.rotate(img, cv2.ROTATE_180)
        
    if orientation != 8 and orientation != 1 and orientation != 6 and orientation != 3:
        return None

    return img

def rotate_back_image(img, img_name):
    try:
        with exiftool.ExifTool() as et:
            orientation = et.get_metadata(img_name)["EXIF:Orientation"]
    except KeyError:
        return None

    if orientation == 8:
        img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    if orientation == 6:
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    if orientation == 3:
        img = cv2.rotate(img, cv2.ROTATE_180)

    if orientation != 8 and orientation != 1 and orientation != 6 and orientation != 3:
        return None

    return img