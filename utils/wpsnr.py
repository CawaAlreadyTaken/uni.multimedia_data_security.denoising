import numpy as np
from scipy.signal import convolve2d
from typing import Any
from multiprocessing import Pool

def convolve_channel(args):
    channel, w = args
    return convolve2d(channel, np.rot90(w, 2), mode='valid')

def wpsnr(img1: Any, img2: Any) -> float:
    img1 = np.float32(img1) / 255.0
    img2 = np.float32(img2) / 255.0
    
    difference = img1 - img2
    same = not np.any(difference)
    if same:
        return 9999999
    
    w = np.genfromtxt('utils/csf.csv', delimiter=',')
    
    with Pool(processes=3) as pool:
        ew_r, ew_g, ew_b = pool.map(convolve_channel, [(difference[:, :, i], w) for i in range(3)])
    
    ew = (ew_r + ew_g + ew_b) / 3.0
    
    decibels = 20.0 * np.log10(1.0 / np.sqrt(np.mean(ew ** 2)))
    return decibels
