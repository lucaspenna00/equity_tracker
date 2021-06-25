import requests
from zipfile import ZipFile
from io import BytesIO
import time
from tqdm import tqdm

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
            raise Exception(f"Error downloading data from CVM and year: {year}. Error code: {status}")
        
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
            raise Exception(f"Error downloading data from CVM and year: {year}. Error code: {status}")
        
        time.sleep(5)