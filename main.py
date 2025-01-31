import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time
from contextlib import contextmanager

# Decorator to time function execution
def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Execution time for {func.__name__}: {end_time - start_time:.4f} seconds")
        return result
    return wrapper

# Context manager for handling file operations
@contextmanager
def file_handler(file_path, mode):
    try:
        file = open(file_path, mode)
        yield file
    finally:
        file.close()

# Load the cleaned data using context manager
file_path = "cleaned_data.csv"
with file_handler(file_path, "r") as file:
    df = pd.read_csv(file)

# Ensure Date column is in datetime format
df["Date"] = pd.to_datetime(df["Date"])

# Sort data by date
df = df.sort_values(by="Date")

@timing_decorator
def calculate_daily_change(df):
    df["Daily Change %"] = df["Close"].pct_change() * 100
    return df

df = calculate_daily_change(df)

# Identify top-performing and underperforming stocks
try:
    highest_close = df.loc[df["Close"].idxmax()]
    lowest_close = df.loc[df["Close"].idxmin()]
    print("Top-performing stock:")
    print(highest_close[["Date", "Close"]])
    print("\nUnderperforming stock:")
    print(lowest_close[["Date", "Close"]])
except Exception as e:
    print("Error in identifying top-performing and underperforming stocks:", e)

# Determine volatility (standard deviation of daily percentage change)
try:
    volatility = df["Daily Change %"].std()
    print("\nStock Volatility (Standard Deviation of Daily Change %):", round(volatility, 2))
except Exception as e:
    print("Error in calculating volatility:", e)

# Group data by stock symbol to compute average trading volume and closing prices
if "Stock Symbol" in df.columns:
    try:
        grouped_data = df.groupby("Stock Symbol")[["Shares Traded", "Close"]].mean()
        print("\nAverage Trading Volume and Closing Prices by Stock Symbol:")
        print(grouped_data)
    except Exception as e:
        print("Error in grouping data:", e)

# Analyze trends across specific timeframes - monthly
df["Year-Month"] = df["Date"].dt.to_period("M")
monthly_trends = df.groupby("Year-Month")["Close"].mean()
print("\nMonthly Average Closing Prices:")
print(monthly_trends)

# Plot the closing prices of selected stocks over time
plt.figure(figsize=(12, 6))
plt.plot(df["Date"], df["Close"], label="Closing Price")
plt.xlabel("Date")
plt.ylabel("Closing Price")
plt.title("Stock Closing Prices Over Time")
plt.legend()
plt.show()

# Create bar charts for trading volumes
if "Stock Symbol" in df.columns:
    plt.figure(figsize=(12, 6))
    df.groupby("Stock Symbol")["Shares Traded"].sum().plot(kind='bar')
    plt.xlabel("Stock Symbol")
    plt.ylabel("Total Trading Volume")
    plt.title("Total Trading Volume by Stock")
    plt.xticks(rotation=45)
    plt.show()

# Use a heatmap to visualize correlations between stocks
if "Stock Symbol" in df.columns:
    pivot_df = df.pivot(index="Date", columns="Stock Symbol", values="Close")
    correlation_matrix = pivot_df.corr()
    plt.figure(figsize=(10, 6))
    sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Stock Correlation Heatmap")
    plt.show()
