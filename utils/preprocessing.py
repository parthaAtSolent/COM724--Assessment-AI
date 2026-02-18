import pandas as pd
import numpy as np
from scipy.stats.mstats import winsorize
from scipy.stats import yeojohnson
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import warnings
import os

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)


def preprocessing(data: pd.DataFrame) -> pd.DataFrame:
    df = data.copy()

    # Date handling
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)

    # Fill missing values
    df.ffill(inplace=True)
    # df.bfill(inplace=True)
    df.drop_duplicates(inplace=True)

    # Numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    # Winsorization
    for col in numeric_cols:
        lower = df[col].quantile(0.05)
        upper = df[col].quantile(0.95)
        df[col] = df[col].clip(lower, upper)

    # # Yeo-Johnson (replace originals)
    # for col in numeric_cols:
    #     transformed, _ = yeojohnson(df[col])
    #     df[col] = transformed

    # # Moving averages
    # for w in [5, 10, 20, 50]:
    #     df[f'MA_{w}'] = df['Close'].rolling(w).mean()

    # # Lag features
    # for lag in [1, 2, 3, 5, 10, 20, 50]:
    #     for col in ['Close', 'Volume', 'High', 'Low']:
    #         df[f'{col}_lag_{lag}'] = df[col].shift(lag)

    # # Price-based features
    # df['High_Low_Ratio'] = df['High'] / df['Low']
    # df['Close_Open_Ratio'] = df['Close'] / df['Open']
    # df['Price_Range'] = df['High'] - df['Low']
    # df['Body_Size'] = abs(df['Close'] - df['Open'])
    # df['Price_Position'] = (df['Close'] - df['Low']) / (df['High'] - df['Low'])

    # # Time features
    # idx = df.index
    # df['Day_of_Week'] = idx.dayofweek
    # df['Month'] = idx.month
    # df['Quarter'] = idx.quarter
    # df['Year'] = idx.year
    # df['Week_of_Year'] = idx.isocalendar().week.astype(int)
    # df['Day_of_Year'] = idx.dayofyear
    # df['Month_End'] = idx.is_month_end.astype(int)
    # df['Month_Begin'] = (idx.day == 1).astype(int)

    # # Returns & volatility
    # df['Daily_Return'] = df['Close'].pct_change()
    # df['Log_Return'] = np.log(df['Close'] / df['Close'].shift(1))
    # df['Volatility_5'] = df['Daily_Return'].rolling(5).std()
    # df['Volatility_10'] = df['Daily_Return'].rolling(10).std()
    # df['Volatility_20'] = df['Daily_Return'].rolling(20).std()

    # # Targets
    # df['Target_Change'] = df['Close'].shift(-1) - df['Close']
    # df['Target'] = df['Target_Change']
    # df['Target_Binary'] = (df['Target_Change'] > 0).astype(int)

    # # Final cleanup
    # df.ffill(inplace=True)
    # df.bfill(inplace=True)
    # df.dropna(inplace=True)
    # df.drop_duplicates(inplace=True)

    # # Column whitelist
    # final_columns = [
    #     'High', 'Low', 'Open', 'Volume', 'Close',
    #     'MA_5', 'MA_10', 'MA_20', 'MA_50',
    #     'Close_lag_1', 'Volume_lag_1', 'High_lag_1', 'Low_lag_1',
    #     'Close_lag_2', 'Volume_lag_2', 'High_lag_2', 'Low_lag_2',
    #     'Close_lag_3', 'Volume_lag_3', 'High_lag_3', 'Low_lag_3',
    #     'Close_lag_5', 'Volume_lag_5', 'High_lag_5', 'Low_lag_5',
    #     'Close_lag_10', 'Volume_lag_10', 'High_lag_10', 'Low_lag_10',
    #     'Close_lag_20', 'Volume_lag_20', 'High_lag_20', 'Low_lag_20',
    #     'Close_lag_50', 'Volume_lag_50', 'High_lag_50', 'Low_lag_50',
    #     'High_Low_Ratio', 'Close_Open_Ratio', 'Price_Range',
    #     'Body_Size', 'Price_Position',
    #     'Day_of_Week', 'Month', 'Quarter', 'Year',
    #     'Week_of_Year', 'Day_of_Year', 'Month_End', 'Month_Begin',
    #     'Daily_Return', 'Volatility_5', 'Volatility_10', 'Volatility_20',
    #     'Log_Return', 'Target', 'Target_Change', 'Target_Binary'
    # ]

    # df = df[final_columns].copy()

    # print("Total Columns - ", df.columns.tolist())

    return df
