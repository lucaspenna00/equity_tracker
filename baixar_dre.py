from equity_research.equity_research import EquityResearch
from datetime import date

ticker=input("[USER] Digite o Ticker desejado: ")
ano=int(input("[USER] Digite o ano: "))
mes=int(input("[USER] Digite o mes: "))
dia=int(input("[USER] Digite o dia: "))

eqr = EquityResearch()
eqr.get_DRE(ticker, date(ano,mes,dia))
print("[INFO] File generated in log file. Enjoy it!")