from datetime import datetime, timedelta
import pandas as pd
from dateutil.relativedelta import relativedelta, MO

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

# Accounts to include
accounts_to_include = [
    '66TX99MF', '66TX99JP', '66TX99CB', '66TX99DS', '66TX99JM',
    '66TX99JK', '66TX99CP', '66TX99RC', '66TX99JR', '66TX99DJ',
    '66EG99OL', '66EG99WY', '66TX99KS', '66TX99OC', '66TX99OX', '66TX99OG'
]

# accounts_to_include = [
#     '66TX99ART'
# ]

# Filter accounts and keep only the required columns
df = df[df['AccountNumber'].isin(accounts_to_include)]

# Drop columns
columns_to_keep = ['AccountNumber', 'TradeMarketValue', 'SettleMarketValue']
df = df[columns_to_keep]

# Group and sum
grouped_df = df.groupby('AccountNumber').sum().fillna(0)

# Add new columns
grouped_df = grouped_df.assign(
    LongTradeMarketValue=df[df['TradeMarketValue'] > 0].groupby('AccountNumber')['TradeMarketValue'].sum(),
    ShortTradeMarketValue=df[df['TradeMarketValue'] < 0].groupby('AccountNumber')['TradeMarketValue'].sum(),
    LongSettleMarketValue=df[df['SettleMarketValue'] > 0].groupby('AccountNumber')['SettleMarketValue'].sum(),
    ShortSettleMarketValue=df[df['SettleMarketValue'] < 0].groupby('AccountNumber')['SettleMarketValue'].sum()
)

# Rename the columns
grouped_df = grouped_df.rename(columns={
    'LongTradeMarketValue': 'Long Trade Market Value',
    'ShortTradeMarketValue': 'Short Trade Market Value',
    'LongSettleMarketValue': 'Long Settle Market Value',
    'ShortSettleMarketValue': 'Short Settle Market Value',
})



# Drop the original columns
grouped_df = grouped_df.drop(columns=['TradeMarketValue', 'SettleMarketValue'])

# Account info
account_info = {
    '66TX99MF': ('Fixed Income - Miscellaneous', 'Trading'),
    '66TX99JP': ('Jospeh Polverino', 'Trading'),
    '66TX99CB': ('Craig B', 'Trading'),
    '66TX99DS': ('Duncan Smith DS Muni', 'Trading'),
    '66TX99JM': ('John Matsikoudis Muni', 'Trading'),
    '66TX99JK': ('Johnathan Katouff - Corp', 'Trading'),
    '66TX99CP': ('Chris Patronis - Repo', 'Trading'),
    '66TX99RC': ('Ryan Cocco  - CD', 'Trading'),
    '66TX99JR': ('Jason Rogan RP', 'Trading'),
    '66TX99DJ': ('Doug Jones MUNI', 'Trading'),
    '66EG99OL': ('Wayne Yagman - Odd Lot', 'Trading'),
    '66EG99WY': ('Wayne Yagman', 'Trading'),
    '66TX99KS': ('Kirk Sauer', 'Trading'),
    '66TX99OC': ('Oliver Curri', 'Trading'),
    '66TX99OX': ('Emerging Market Bonds', 'Trading'),
    '66TX99OG': ('Emerging Market Bonds', 'Trading'),
    '66TX99ART': ('Mixed', 'Trading'),

}

# Add Account Name and Account Type columns
grouped_df['Account Name'] = grouped_df.index.map(lambda x: account_info[x][0])
grouped_df['Account Type'] = grouped_df.index.map(lambda x: account_info[x][1])

# Add empty columns
grouped_df['Liquidating Equity'] = ''
grouped_df['T/D Balance'] = ''
grouped_df['Margin Requirements'] = ''
grouped_df['Margin Excess/Call'] = ''
grouped_df['S/D Balance'] = ''

# Reorder columns
columns_order = [
    'Account Name', 'Account Type', 'Liquidating Equity', 
    'Long Trade Market Value', 'Short Trade Market Value', 'T/D Balance', 
    'Margin Requirements', 'Margin Excess/Call', 'Long Settle Market Value', 
    'Short Settle Market Value', 'S/D Balance'
]
grouped_df = grouped_df[columns_order]


def resize_columns(df, worksheet):
    column_len = max(df.index.astype(str).str.len().max(), len('AccountNumber') + 2)
    worksheet.set_column(0, 0, column_len * 1.2)
    for i, col in enumerate(df.columns, start=1):
        column_len = max(df[col].astype(str).str.len().max(), len(col) + 2)
        worksheet.set_column(i, i, column_len * 1.2)

def write_total_row(df, worksheet, workbook, currency_format):
    # Get the last row
    last_row = worksheet.dim_rowmax + 1

    # Write 'Total' in column A and format the entire row
    format_total_row = workbook.add_format({'bold': True, 'bg_color': '#C6EFCE'})

    # Write 'Total' in column A with formatting
    worksheet.write(last_row, 0, 'Total', format_total_row)

    # Create a new format for the total row that includes the currency format
    total_currency_format = workbook.add_format({'bold': True, 'bg_color': '#C6EFCE', 'num_format': '#,##0.00_);[Red](#,##0.00)'})

    # Calculate the totals for each column and write them in the 'Total' row with formatting
    for col in range(1, len(df.columns)+1):
        if col not in {3, 6, 7, 8}:  # Skip the specified columns
            total = df.iloc[:, col-1].sum()
            if pd.notnull(total) and isinstance(total, (int, float)):
                worksheet.write_number(last_row, col, total, total_currency_format)
        else:
            worksheet.write(last_row, col, '', format_total_row)

# Save to Excel
with pd.ExcelWriter(f"DailyPL_Summary_{date_string}.xlsx", engine='xlsxwriter') as writer:
    grouped_df.to_excel(writer, sheet_name='Summary', index=True)
    worksheet = writer.sheets['Summary']
    workbook = writer.book

    header_format = workbook.add_format({
        'bold': True,
        'font_color': '#1F497D',
        'bg_color': '#FFFFFF',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
        'font_size': 14
    })

    currency_format = workbook.add_format({
        'num_format': '#,##0.00_);[Red](#,##0.00)'})

    for col_num, value in enumerate(['AccountNumber'] + list(grouped_df.columns.values)):
        worksheet.write(0, col_num, value, header_format)

    for row_num in range(1, len(grouped_df)+1):
        worksheet.write(row_num, 0, grouped_df.index[row_num-1], currency_format)
        for col_num in range(1, len(grouped_df.columns)+1):
            value = grouped_df.iloc[row_num-1, col_num-1]
            if pd.notnull(value):
                if isinstance(value, (int, float)):
                    worksheet.write_number(row_num, col_num, value, currency_format)
                else:
                    worksheet.write(row_num, col_num, value, currency_format)
    
    resize_columns(grouped_df, worksheet)
    write_total_row(grouped_df, worksheet, workbook, currency_format)

print(f"Excel report saved as DailyPL_Summary_{date_string}.xlsx")