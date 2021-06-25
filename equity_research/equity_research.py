import pandas as pd
from datetime import datetime

class EquityResearch():

    def __init__(self):

        self.init = False
        self.from_ticker_to_cnpj = pd.read_csv("input/from_ticker_to_cnpj.csv", sep=',')

    def get_cnpj_from_ticker(self, ticker):

        cnpj = self.from_ticker_to_cnpj[self.from_ticker_to_cnpj['security'] == ticker]

        if cnpj.shape[0] > 0:
            cnpj = cnpj['CNPJ'].iloc[0]
        else:
            raise Exception("CPNJ not found. Verify the if the ticker passed as an argument is correct.")

        return cnpj

