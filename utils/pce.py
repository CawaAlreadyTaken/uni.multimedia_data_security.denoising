import numpy as np

def pce_color(cc: np.ndarray, neigh_radius: int = 2) -> float:
    """
    Compute the PCE (Peak-to-Correlation-Energy) on the 2D cross-correlation map.

    :param cc: 2D cross-correlation map
    :param neigh_radius: radius around the peak to be ignored while computing floor energy
    :return: PCE value
    """
    assert (cc.ndim == 2)
    assert (isinstance(neigh_radius, int))

    # Find global maximum
    max_idx = np.argmax(cc)
    max_y, max_x = np.unravel_index(max_idx, cc.shape)
    peak_height = cc[max_y, max_x]

    # Create a copy to zero out the region around the peak
    cc_nopeaks = cc.copy()
    
    # Safely zero-out the neighborhood around the peak
    y1 = max(0, max_y - neigh_radius)
    y2 = min(cc.shape[0], max_y + neigh_radius + 1)
    x1 = max(0, max_x - neigh_radius)
    x2 = min(cc.shape[1], max_x + neigh_radius + 1)
    cc_nopeaks[y1:y2, x1:x2] = 0

    # Compute the "floor" energy
    pce_energy = np.mean(cc_nopeaks ** 2)

    # Final PCE
    pce_value = (peak_height ** 2) / pce_energy * np.sign(peak_height)
    return pce_value

def pce(cc: np.ndarray, neigh_radius: int = 2):
    """
    PCE position and value
    :param cc: as from crosscorr2d
    :param neigh_radius: radius around the peak to be ignored while computing floor energy
    :return: {'peak':(y,x), 'pce': peak to floor ratio, 'cc': cross-correlation value at peak position
    """
    assert (cc.ndim == 2)
    assert (isinstance(neigh_radius, int))

    #out = dict()

    max_idx = np.argmax(cc.flatten())
    max_y, max_x = np.unravel_index(max_idx, cc.shape)
    peak_height = cc[-1, -1]


    cc_nopeaks = cc.copy()
    cc_nopeaks[max_y - neigh_radius:max_y + neigh_radius, max_x - neigh_radius:max_x + neigh_radius] = 0

    pce_energy = np.mean(cc_nopeaks.flatten() ** 2)

#    out['peak'] = (max_y, max_x)
    out = (peak_height ** 2) / pce_energy * np.sign(peak_height)
#    out['cc'] = peak_height

    return out


def pce_original(cc: np.ndarray, neigh_radius: int = 2) -> dict:
    """
    PCE position and value
    :param cc: as from crosscorr2d
    :param neigh_radius: radius around the peak to be ignored while computing floor energy
    :return: {'peak':(y,x), 'pce': peak to floor ratio, 'cc': cross-correlation value at peak position
    """
    assert (cc.ndim == 2)
    assert (isinstance(neigh_radius, int))

    out = dict()

    max_idx = np.argmax(cc.flatten())
    max_y, max_x = np.unravel_index(max_idx, cc.shape)

    peak_height = cc[max_y, max_x]

    cc_nopeaks = cc.copy()
    cc_nopeaks[max_y - neigh_radius:max_y + neigh_radius, max_x - neigh_radius:max_x + neigh_radius] = 0

    pce_energy = np.mean(cc_nopeaks.flatten() ** 2)

    out['peak'] = (max_y, max_x)
    out['pce'] = (peak_height ** 2) / pce_energy * np.sign(peak_height)
    out['cc'] = peak_height

    return out
