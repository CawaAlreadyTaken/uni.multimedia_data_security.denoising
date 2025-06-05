import cv2
import exiftool

def rotate_image(img, img_name):
    with exiftool.ExifTool() as et:
        width, height = img.shape[1], img.shape[0]
        if "EXIF:Orientation" not in et.get_metadata(img_name):
            if width < height:
                return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        orientation = et.get_metadata(img_name)["EXIF:Orientation"]

    if orientation == 8:
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    if orientation == 6:
        img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    if orientation == 3:
        img = cv2.rotate(img, cv2.ROTATE_180)
        
    # if orientation != 8 and orientation != 1 and orientation != 6 and orientation != 3:
    if width < height:
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    return img

def rotate_back_image(img, img_name):
    with exiftool.ExifTool() as et:
        if "EXIF:Orientation" not in et.get_metadata(img_name):
            return None
        orientation = et.get_metadata(img_name)["EXIF:Orientation"]
    if orientation == 8:
        img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    if orientation == 6:
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    if orientation == 3:
        img = cv2.rotate(img, cv2.ROTATE_180)

    if orientation != 8 and orientation != 1 and orientation != 6 and orientation != 3:
        return None

    return img