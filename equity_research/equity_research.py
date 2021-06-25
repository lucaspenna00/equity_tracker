import pandas as pd
from datetime import datetime
import logging
from pathlib import Path

class EquityResearch():

    def __init__(self, ibov=True):
        p = Path("log")
        p.mkdir(exist_ok=True)
        logging.basicConfig( filename="log/equity_research.log", filemode='w+', level=logging.DEBUG, format= '%(asctime)s - %(levelname)s - %(message)s')

        if ibov:
            sheet_name="IBOVCNPJ"
        else:
            sheet_name="ALLCNPJ"

        self.from_ticker_to_cnpj = pd.read_excel("input/from_ticker_to_cnpj.xlsx", sheet_name=sheet_name)

    def get_all_tickers(self):
        return self.from_ticker_to_cnpj['security'].unique().tolist()

    def get_cnpj_from_ticker(self, ticker):
        cnpj = self.from_ticker_to_cnpj[self.from_ticker_to_cnpj['security'] == ticker]
        if cnpj.shape[0] > 0:
            cnpj = cnpj['CNPJ'].iloc[0]
        else:
            error_msg = f"[get_cnpj_from_ticker] CPNJ for {ticker} not found. Verify the if the ticker passed as an argument is correct."
            logging.error(error_msg)
            raise Exception(error_msg)
        return cnpj

    
    

