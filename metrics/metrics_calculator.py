from joblib import Parallel, delayed
import multiprocessing
import os
import glob
import json
import cv2
import numpy as np

from utils.constants import BASEPATH, FINGERPRINTSPATH
from utils.cross_correlation import crosscorr_2d_color
from utils.rotate_image import rotate_image
from utils.pce import pce_color
from utils.ccn import ccn_fft
from utils.wpsnr import wpsnr

def compute_metrics(original_path, anonymized_path, fingerprint):
    """
    Legge le due immagini, esegue le 5 computazioni e
    restituisce (nome_file, dizionario_risultati).
    Se qualcosa va storto (file non esistente, immagine None, ecc.),
    restituisce None in modo da poterlo filtrare.
    """
    if not os.path.exists(anonymized_path):
        return None

    original = cv2.imread(original_path)
    if original is None:
        return None
    
    anonymized = cv2.imread(anonymized_path)
    if anonymized is None:
        return None

    original = rotate_image(original.astype(np.float32), original_path)
    anonymized = rotate_image(anonymized.astype(np.float32), original_path)

    # Calcoli in sequenza (singolo processo).
    results = {}
    results['wpsnr'] = wpsnr(original, anonymized)
    results['initial_pce'] = pce_color(crosscorr_2d_color(original, fingerprint))
    results['pce'] = pce_color(crosscorr_2d_color(anonymized, fingerprint))
    results['initial_ccn'] = ccn_fft(original, fingerprint)
    results['ccn'] = ccn_fft(anonymized, fingerprint)

    # Restituisce (nomefile, results) dove nomefile è il basename dell'originale
    return (os.path.basename(original_path), results)

def main(chosen_devices: list[str], anonymized_images: str):
    # Numero di job paralleli = numero core; puoi modificarlo a piacere
    n_jobs = multiprocessing.cpu_count()

    for device in chosen_devices:
        # Lista dei file originali
        files = sorted(glob.glob(BASEPATH + 'D' + device + '/nat/*.*'))
        
        # Carichiamo il fingerprint in float32 e lo replichiamo sui 3 canali
        fp_path = os.path.join(FINGERPRINTSPATH, f'Fingerprint_D{device}.npy')
        fingerprint = np.load(fp_path).astype(np.float32)
        fingerprint = np.repeat(fingerprint[..., np.newaxis], 3, axis=2)

        # Verifica esistenza della cartella con le immagini anonimizzate
        if not os.path.exists(anonymized_images):
            print(f"{anonymized_images} folder does not exist")
            return

        print(f"\n** Elaboro dispositivo D{device} **")

        # Definiamo la lista di job da passare in parallelo
        tasks = []
        for original_path in files:
            # Costruisci il path all'immagine anonimizzata corrispondente
            anonymized_path = os.path.join(anonymized_images, f'D{device}', os.path.basename(original_path))
            tasks.append((original_path, anonymized_path))

        # Eseguiamo in parallelo
        results = Parallel(n_jobs=n_jobs)(
            delayed(compute_metrics)(orig, anon, fingerprint) 
            for (orig, anon) in tasks
        )

        # Filtra i None (file che non esistevano o immagini non valide)
        results = [r for r in results if r is not None]

        # Convertiamo la lista in un dizionario {filename: metrics}
        data = {filename: metrics for (filename, metrics) in results}

        # Salvataggio su file JSON
        output_file = os.path.join(anonymized_images, f'D{device}', 'metrics.json')
        print("Salvo il file:", output_file)
        with open(output_file, "w", encoding="utf-8") as file_json:
            json.dump(data, file_json, indent=4, ensure_ascii=False)

        print(f" -> Completato D{device}, {len(data)} file elaborati.")
