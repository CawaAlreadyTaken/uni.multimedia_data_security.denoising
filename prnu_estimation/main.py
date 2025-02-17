from utils.extraction import extract_multiple_aligned
from multiprocessing import cpu_count
from scipy.io import savemat
import numpy as np
import exiftool
import glob
import cv2

basepath='/media/SSD_mmlab/VISION_IMAGES/' # dataset root

def estimate():

    devices = sorted(glob.glob(basepath+'D*'))
    # print(devices)

    for device_path in devices:
        files = sorted(glob.glob(device_path + '/flat/*.*'))
        K_k = []
        imgs = []
        group_size = 30
        idx_1 = 0
        idx_2 = 0
        for img_name in files:
            print(img_name)
            img = cv2.imread(img_name)
            try:
                with exiftool.ExifTool() as et:
                    orientation = et.get_metadata(img_name)["EXIF:Orientation"]
                if orientation == 8:
                    img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
                if orientation == 6:
                    img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
                if orientation == 3:
                    img = cv2.rotate(img, cv2.ROTATE_180)
        
                if orientation != 8 and orientation != 1 and orientation != 6 and orientation != 3:
                    continue

                imgs += [img.astype(dtype=np.uint8)]
                
            except:
                if np.shape(img)[0]<np.shape(img)[1]:
                    imgs += [img.astype(dtype=np.uint8)]

        if not len(imgs):
            for img_name in files:
                img = cv2.imread(img_name)
                if np.shape(img)[0]<np.shape(img)[1]:
                    imgs += [img.astype(dtype=np.uint8)]
        
        print('compute fingerprint', device_path[-3:], ' with: ', len(imgs), 'IMAGES')
        K_k += [extract_multiple_aligned(imgs, processes=cpu_count(), sigma=3)]
        K_k = np.stack(K_k, 0)

        
        del imgs
        K = np.squeeze(K_k, axis=0)
        mdic1 = {"fing": K}
        out_name = 'fingerprints/Fingerprint_' + device_path[-3:] + '.mat'
        savemat(out_name, mdic1)

if __name__ == "__main__":
    estimate()
