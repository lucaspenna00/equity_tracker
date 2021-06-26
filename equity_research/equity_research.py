import pandas as pd
from datetime import datetime
import logging
from pathlib import Path
import unidecode
import warnings

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

    def _transform_string(self, x):
        x = unidecode.unidecode(x)
        x = x.replace(" de "," ").replace(" da "," ").replace(" das ", " ").replace(" dos ", " ").replace(" do ", " ")
        x = x.lower()
        return x

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

    def get_net_revenue(self, ticker, date_arg):
        cnpj = self.get_cnpj_from_ticker(ticker)
        filename=f"data/trimestral/{date_arg.year}/itr_cia_aberta_DRE_con_{date_arg.year}.csv"
        df = pd.read_csv(filename, encoding='iso-8859-1', sep=';') 
        filename=f"data/trimestral/{date_arg.year}/itr_cia_aberta_DRE_ind_{date_arg.year}.csv"
        df_ind = pd.read_csv(filename, encoding='iso-8859-1', sep=';')
        df = df.append(df_ind)

        if cnpj in df['CNPJ_CIA'].tolist():
            df = df[df['CNPJ_CIA'] == cnpj]
            df = df[df['DT_REFER'] == str(date_arg)]
            date_max_init_exer = df['DT_INI_EXERC'].max()
            df = df[df['DT_INI_EXERC'] == date_max_init_exer]
            df['DS_CONTA'] = df['DS_CONTA'].apply(lambda x: self._transform_string(x))
                    
            if ticker == 'BRAP4' or ticker == "BBSE3":
                df = df[df['DS_CONTA'] == 'resultado equivalencia patrimonial']
            elif ticker =="IRBR3":
                df = df[df['DS_CONTA'] == 'receitas operacoes']
            else:
                if 'receita venda bens e/ou servicos' in df['DS_CONTA'].tolist():
                    df = df[df['DS_CONTA'] == 'receita venda bens e/ou servicos']

                elif 'resultado bruto intermediacao financeira' in df['DS_CONTA'].tolist():
                    df = df[df['DS_CONTA'] == 'resultado bruto intermediacao financeira']
                else:
                    error_msg = f"[get_net_revenue] Net revenue for {ticker} in {date_arg} not found."
                    logging.error(error_msg)
                    raise Exception(error_msg)

            df = df[df['VL_CONTA'] != 0.0]

            if df.shape[0] > 0:
                net_revenue = df['VL_CONTA'].iloc[0]
            else:
                net_revenue = 0.0
                warning_msg = f"[get_net_revenue] net revenue 0.0 for {ticker} in {date_arg}."
                logging.warning(warning_msg)
                warnings.warn(warning_msg)
        else:
            error_msg = f"[get_net_revenue] cnpj for {ticker} in {date_arg} not found."
            logging.error(error_msg)
            raise Exception(error_msg)
            
        return net_revenue

    
    

