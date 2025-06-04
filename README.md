# uni.multimedia_data_security.denoising
This is the project repository for the multimedia data security course

## Installation
Create a virtual environment and install the requirements:
```bash
$ python3 -m venv .venv
$ source .venv/bin/activate

$ pip install -r requirements.txt
```

It is important to modify the constant variables in the file `utils/constants.py ` to change the `BASEPATH` to the local path of the dataset.

## Menu

After running the `main.py` file:
```bash
python main.py
```

the following menu will be displayed in the terminal:
```bash
=== MAIN MENU ===

Please choose an option:
1) Generate fingerprints
2) Anonymize images
3) Show metrics
4) Generate graphs
h) Help
q) Quit

Enter your choice:
```

For every option that requires specifying the algorithm and the devices, the following menus will be shown:
```bash
===== ANONYMIZER MENU =====

1) Fingerprint Removal
2) Median Filtering
3) APD2
all) Apply all three algorithms
h) Show this menu description again
q) Quit anonymizer, go back
Select an option: 

Enter the device number(s) between 1 and 35 to process.
You can specify them in these ways:
 - Single device (e.g. '8')
 - Multiple comma-separated devices (e.g. '8,9,10')
 - A range with a dash (e.g. '6-10')
Or any combination (e.g. '5,7,10-12').
Your choice:
```

## Credits
Multimedia Data Secuity - Università degli Studi di Trento

Annachiata Fortuna\
Daniele Cabassi\
Enrico Carnelos

correggi gli errori grammaticali senza cambiare la forma