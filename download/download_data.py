import requests
from zipfile import ZipFile
from io import BytesIO
import time
from tqdm import tqdm
import logging
from pathlib import Path

p = Path("log")
p.mkdir(exist_ok=True)

logging.basicConfig( filename="log/download_data.log", filemode='w+', level=logging.DEBUG, format= '%(asctime)s - %(levelname)s - %(message)s')

def download_trimestral_data_from_cvm(year_start, year_end):
    
    years = list(range(year_start, year_end+1))
    for year in tqdm(years):
        
        url = f'http://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/ITR/DADOS/itr_cia_aberta_{year}.zip'
        
        r = requests.get(url, stream=True)
        status = r.status_code
        
        if status == 200:
            z = ZipFile(BytesIO(r.content))    
            z.extractall(f"data/trimestral/{year}/")
        else:
            error_msg = f"[download_trimestral_data_from_cvm] Error downloading trimestral data from CVM and year: {year}. Error code: {status}"
            logging.error(error_msg)
            raise Exception(error_msg)
        
        time.sleep(5)

def download_anual_data_from_cvm(year_start, year_end):
    
    years = list(range(year_start, year_end+1))
    for year in tqdm(years):
        
        url = f'http://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/dfp_cia_aberta_{year}.zip'
        
        r = requests.get(url, stream=True)
        status = r.status_code
        
        if status == 200:
            z = ZipFile(BytesIO(r.content))    
            z.extractall(f"data/anual/{year}/")
        else:
            error_msg = f"[download_anual_data_from_cvm] Error downloading anual data from CVM and year: {year}. Error code: {status}"
            logging.error(error_msg)
            raise Exception(error_msg)
        
        time.sleep(5)