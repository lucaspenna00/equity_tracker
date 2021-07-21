from download import download_data
import argparse
from datetime import datetime
import psutil
import simfin as sf
from pathlib import Path

NECESSARY_SPACE= 10 # in GB
GB = 1000000000.0

def download_cvm():

    global NECESSARY_SPACE
    global GB
    global args

    space_in_gb = psutil.disk_usage(".").free/GB
    if space_in_gb < NECESSARY_SPACE: 
        raise Exception(f"You don't have enough space. This repository needs approximately 10G to work properly. You have just {space_in_gb} GB free in your hard disk.")
    else:
        answer = input(f"[INFO] Space is not a problem. You have {space_in_gb} GB in your hard disk. Do you want to proceed? [Y/n] ")
        if answer == "Y" or answer == "y":
            date_init = int(input("Enter the start year to download CVM data [ 2011<=year<=2021 ]:"))
            date_final = int(input("Enter the final year to download CVM data [ 2011<=year<=2021 ]:"))
            current_year = datetime.now().year
            if date_init < 2011:
                raise Exception("There is no CVM data before 2011.")
            elif date_final > current_year:
                raise Exception(f"There is no CVM data after {current_year}.")
            else:
                print("[INFO] Downloading trimestral data from CVM...")
                download_data.download_trimestral_data_from_cvm(date_init, date_final)
                print("[INFO] Downloading anual data from CVM...")
                download_data.download_anual_data_from_cvm(date_init, date_final)
        else:
            print("[INFO] Operation canceled.")

def setup_simfin():
    answer = input(f"[INFO] SimFin version currently installed is: {sf.__version__}. Do you want to proceed? [Y/n]")
    if answer == "Y" or answer == "y":
        print("[INFO] Setting default data directory...")
        p = Path("data")
        p.mkdir(exist_ok=True)
        p = Path("data/us")
        p.mkdir(exist_ok=True)
        sf.set_data_dir('data/us/')
        print("[INFO] Setting default SimFin api_key to FREE...")
        sf.set_api_key(api_key='free')
    else:
        print("[INFO] Operation canceled.")


answer = input("[INFO] Welcome to Equity Tracker installer.\nDo you want to install CVM data? [Y/n]")
if answer == "Y" or answer == "y":
    download_cvm()

answer = input("[INFO] Do you want to install SimFin US data? [Y/n]")
if answer == "Y" or answer == "y":
    setup_simfin()
