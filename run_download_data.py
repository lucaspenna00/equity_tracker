from download import download_data
import argparse
from datetime import datetime
import psutil

NECESSARY_SPACE= 10 # in GB
GB = 1000000000.0

parser = argparse.ArgumentParser()
parser.add_argument("date_init", help="date init for CVM data download", type=int)
parser.add_argument("date_final", help="date final for CVM data download", type=int)
args = parser.parse_args()

def download():

    global NECESSARY_SPACE
    global GB
    global args

    space_in_gb = psutil.disk_usage(".").free/GB
    if space_in_gb < NECESSARY_SPACE: 
        raise Exception(f"You don't have enough space. The repository needs approximately 10G to work properly. You have just {space_in_gb} GB free in your hard disk.")
    else:
        answer = input(f"[INFO] Space is not a problem. You have {space_in_gb} in your hard disk. Do you want to proceed? [Y/n] ")
        if answer == "Y" or answer == "y":
            current_year = datetime.now().year
            if args.date_init < 2011:
                raise Exception("There is no CVM data before 2011.")
            elif args.date_final > current_year:
                raise Exception(f"There is no CVM data after {current_year}")
            else:
                print("[INFO] Downloading trimestral data from CVM...")
                download_data.download_trimestral_data_from_cvm(args.date_init, args.date_final)
                print("[INFO] Downloading anual data from CVM...")
                download_data.download_anual_data_from_cvm(args.date_init, args.date_final)
        else:
            print("[INFO] Operation canceled.")

download()

