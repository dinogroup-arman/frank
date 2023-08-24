from datetime import datetime, timedelta
import pandas as pd
from dateutil.relativedelta import relativedelta, MO
import numpy as np

# Get today's date
today = datetime.now()

# Calculate the difference in days to get the previous day
if today.weekday() == 0:  # Monday
    previous_day = today - timedelta(days=3)  # Get the date of the previous Friday
else:
    previous_day = today - timedelta(days=1)  # Get the date of the previous day

date_string = previous_day.strftime("%Y%m%d")

# Format the previous day as 'YYYYMMDD'

tx_file_name = f"TX_Balance_{20230821}.csv"
eg_file_name = f"EG_Balance_{20230821}.csv"

# Concatenate the dataframes
df = pd.concat([pd.read_csv(tx_file_name), pd.read_csv(eg_file_name)], ignore_index=True)

# Accounts to include
accounts_to_include = [
    '66TX99MF', '66TX99JP', '66TX99CB', '66TX99DS', '66TX99JM',
    '66TX99JK', '66TX99CP', '66TX99RC', '66TX99JR', '66TX99DJ',
    '66EG99OL', '66EG99WY', '66TX99KS', '66TX99OC', '66TX99OX', '66TX99OG'
]

# Filter accounts and keep only the required columns
df = df[df['AccountNumber'].isin(accounts_to_include)]

# Drop columns
columns_to_keep = ['AccountNumber', 'TradeDateCashBalance', 'SettleDateCashBalance', 'LiquidatingEquity', 'HouseRequirement']
df = df[columns_to_keep]

# Group and sum
grouped_df = df.groupby('AccountNumber').sum().fillna(0)

# Define the path and name for the CSV file
csv_file_name = f"balance_{date_string}.csv"

# Export the dataframe to CSV
grouped_df.reset_index().to_csv(csv_file_name, index=False)
