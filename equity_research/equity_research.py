import pandas as pd
from datetime import datetime
import logging
from pathlib import Path
import unidecode
import warnings
import inspect

class EquityResearch():

    def __init__(self, ibov=True):
        p = Path("log")
        p.mkdir(exist_ok=True)
        logging.basicConfig( filename="log/equity_research.log", filemode='w+', level=logging.DEBUG, format= '%(asctime)s - %(levelname)s - %(message)s')

        if ibov:
            sheet_name="IBOVCNPJ"
        else:
            sheet_name="ALLCNPJ"

        self._from_ticker_to_cnpj = pd.read_excel("input/from_ticker_to_cnpj.xlsx", sheet_name=sheet_name)

    def _transform_string(self, x):
        x = unidecode.unidecode(x)
        x = x.replace(" de "," ").replace(" da "," ").replace(" das ", " ").replace(" dos ", " ").replace(" do ", " ")
        x = x.lower()
        return x

    def get_all_tickers(self):
        return self._from_ticker_to_cnpj['security'].unique().tolist()

    def get_cnpj_from_ticker(self, ticker):
        cnpj = self._from_ticker_to_cnpj[self._from_ticker_to_cnpj['security'] == ticker]
        if cnpj.shape[0] > 0:
            cnpj = cnpj['CNPJ'].iloc[0]
        else:
            error_msg = f"[get_cnpj_from_ticker] CPNJ for {ticker} not found. Verify the if the ticker passed as an argument is correct."
            logging.error(error_msg)
            raise Exception(error_msg)
        return cnpj        

    def get_DRE(self, ticker, date_arg, log_enabled=True):
        cnpj = self.get_cnpj_from_ticker(ticker)
        filename=f"data/trimestral/{date_arg.year}/itr_cia_aberta_DRE_con_{date_arg.year}.csv"
        df = pd.read_csv(filename, encoding='iso-8859-1', sep=';') 
        filename=f"data/trimestral/{date_arg.year}/itr_cia_aberta_DRE_ind_{date_arg.year}.csv"
        df_ind = pd.read_csv(filename, encoding='iso-8859-1', sep=';')
        df = df.append(df_ind)

        if cnpj in df['CNPJ_CIA'].tolist():
            df = df[df['CNPJ_CIA'] == cnpj]
            df = df[df['DT_REFER'] == str(date_arg)]
            df = df[df['DT_INI_EXERC'] == df['DT_INI_EXERC'].max()]
            if log_enabled:
                df.to_excel("log/"+ticker+"_dre.xlsx")
        else:
            error_msg = f"[get_net_revenue] cnpj for {ticker} in {date_arg} not found."
            logging.error(error_msg)
            raise Exception(error_msg)
        
        return df

    def _filt_df(self, df, ticker, date_arg, column_based, value_to_filt, func_name):
        if value_to_filt in df[column_based].tolist():
            df = df[df[column_based] == value_to_filt]
        else:
            error_msg = f"[{func_name}] gross revenue for {ticker} in {date_arg} not found."
            logging.error(error_msg)
            raise Exception(error_msg)

        df = df[df['VL_CONTA'] != 0.0]
        if df.shape[0] > 0:
            gross_revenue = df['VL_CONTA'].iloc[0]
        else:
            gross_revenue = 0.0
            warning_msg = f"[{func_name}] gross_revenue is 0.0 for {ticker} in {date_arg}."
            logging.warning(warning_msg)
            warnings.warn(warning_msg)
        return gross_revenue   

    def get_gross_revenue(self, ticker, date_arg):
        this_function_name = inspect.currentframe().f_code.co_name
        df = self.get_DRE(ticker, date_arg, log_enabled=False)
        gross_revenue = self._filt_df(df, ticker, date_arg, "CD_CONTA", "3.01", this_function_name)
        return gross_revenue   

    def get_resultado_bruto(self, ticker, date_arg):
        this_function_name = inspect.currentframe().f_code.co_name
        df = self.get_DRE(ticker, date_arg, log_enabled=False)
        resultado_bruto = self._filt_df(df, ticker, date_arg, "CD_CONTA", "3.03", this_function_name)
        return resultado_bruto

    

    


    
    

