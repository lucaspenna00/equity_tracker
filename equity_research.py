import pandas as pd
import json
from datetime import datetime

class EquityResearch():

    def __init__(self):

        self.init = False

    def _get_sector_by_security(self, security):
        data = json.load(open("data/metadata/map_ativos_setores"))
        for key in data.keys():
            if security in data[key]:
                return key

    def get_all_securities(self):
        data = json.load(open("data/metadata/map_ativos_setores"))
        data = list(data.values())
        securities = [item for sublist in data for item in sublist]
        return securities

    def get_net_revenue(self, ticker, date_arg):
        date_str = date_arg.strftime("%d/%m/%Y")
        sector=self._get_sector_by_security(ticker)
        df_dre = pd.read_excel("data/financial_reports/"+sector+"/"+ticker+"/balanco.xls", skiprows=1, sheet_name=1)
        df_dre.rename({'Unnamed: 0':'descritivo'}, inplace=True, axis=1)
        df_dre.rename({' ':'descritivo'}, inplace=True, axis=1)
        
        if 'Receita Líquida de Vendas e/ou Serviços' in df_dre['descritivo'].tolist():
            net_revenue = df_dre[df_dre['descritivo'] == 'Receita Líquida de Vendas e/ou Serviços'][date_str].tolist()[0]
            #net_revenue = df_dre[df_dre['descritivo'] == 'Receita Líquida de Vendas e/ou Serviços'].iloc[:,1].tolist()[0]
        else:
            if 'Resultado Bruto Intermediação Financeira' in df_dre['descritivo'].tolist():
                net_revenue = df_dre[df_dre['descritivo'] == 'Resultado Bruto Intermediação Financeira'][date_str].tolist()[0]
            else:
                raise Exception("Net revenue not found.")
                
        return net_revenue
    
    def get_book_value(self, ticker, date_arg):

        date_str = date_arg.strftime("%d/%m/%Y")
        sector=self._get_sector_by_security(ticker)
        df_balanco = pd.read_excel("data/financial_reports/"+sector+"/"+ticker+"/balanco.xls", skiprows=1, sheet_name=0)
        df_balanco.rename({'Unnamed: 0':'descritivo'}, inplace=True, axis=1)
        df_balanco.rename({' ':'descritivo'}, inplace=True, axis=1)
        try:
            p_l = df_balanco[df_balanco['descritivo'] == 'Patrimônio Líquido']['31/12/2020'].iloc[0]
            #p_l = df_balanco[df_balanco['descritivo'] == 'Patrimônio Líquido'].iloc[:,1].tolist()[0]
        except:
            p_l = None
            
        return p_l


