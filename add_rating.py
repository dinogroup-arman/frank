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

tx_file_name = f"TX_DailyPL_{date_string}.csv"
eg_file_name = f"EG_DailyPL_{date_string}.csv"

# Concatenate the dataframes
df = pd.concat([pd.read_csv(tx_file_name), pd.read_csv(eg_file_name)], ignore_index=True)


# Rating list
ratings = ['AAA', 'AA+', 'AA', 'AA-', 'A+', 'A', 'A-', 'BBB+', 'BBB', 'BBB-', 'BB+', 'BB', 'BB-', 'B+', 'B', 'B-', 'CCC+', 'CCC', 'CCC-', 'CC', 'C', 'D']

# Add a new column 'rating' and assign random values from the ratings list
df["RATING"] = np.random.choice(ratings, size=len(df))

# Define the conditions
condition1 = (df['SecurityType'].isin(['Corporate Bonds', 'Municipal Bonds', 'Convertible Corporate Bonds']))
condition2 = (df['RATING'].isin(['AAA', 'AA+', 'AA', 'AA-', 'A+', 'A', 'A-', 'BBB+', 'BBB', 'BBB-']))

# Calculate the Margin Requirement based on the conditions
df['Margin Requirements'] = np.where(condition1 & ~condition2, df['TradeMarketValue'] * 0.3,
                                     np.where(condition1 & condition2, df['TradeMarketValue'] * 0.1, np.nan))

# Define the path and name for the CSV file
csv_file_name = "ratings.csv"

# Export the dataframe to CSV
df.to_csv(csv_file_name, index=False)
