# equity_tracker

Equities portfolio based on financial Machine Learning and Black Litterman optimization.
Not tested/improved for linux environments. We will do this.

## 1. First setup

### 1.1 Clone repository

Open terminal/prompt and navigate to the folder you want to install. Then, run:

`
git clone https://github.com/lucaspenna00/equity_tracker
`

### 1.2 Install dependences

Go to **equity_tracker** repository:

`
cd equity_tracker
`

Then, run:

`
pip install -r requeriments.txt
`

### 1.3 Download Data

The source of data is the CVM (SEC equivalent in brazilian market) repository. The data can be obtained for free.
There are plenty of fundamentalist data that we are using in this project, such as Income Statements, Cash Flows and Balance Sheets.
Just ensure you have enough space to download the data (approximately 10GB free in hard disk).

e.g.:

`
python run_download_data.py 2011 2020
`
