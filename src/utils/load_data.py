import os
import json
import pandas as pd
from collections import defaultdict

from src.utils.config import load_config

# Universal

def frame_csv(csv_path):
    """
    open csv file into dataframe
    """
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'])
    df['income'] = df['income'].astype(float)
    df['outcome'] = df['outcome'].astype(float)
    df['bank'] = df['bank'].astype(str)
    df['category'] = df['category'].astype(str)
    df['type'] = df['type'].astype(str)
    df['description'] = df['description'].astype(str)
    df['original_id'] = df['original_id'].astype(str)
    df['participant'] = df['participant'].astype(str).fillna('unknown')
    return df


def load_json(path):
    with open(path, "r") as f:
        lookup_table = json.load(f)
        return lookup_table


def frame_dir(dir_path="data/03--reconciled"):
    """open dir into single dataframe"""
    full_df = pd.DataFrame()
    for file_name in os.listdir(dir_path):
        if file_name.endswith(".csv"):
            file_path = os.path.join(dir_path, file_name)
            df = frame_csv(file_path)
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            full_df = pd.concat([full_df, df], ignore_index=True)
    return full_df


# Categorize specific

def load_dataframes_from_dir(input_dir):
    dataframes = {}
    for csv_file in os.listdir(input_dir):
        if csv_file.endswith(".csv"):
            file_path = os.path.join(input_dir, csv_file)
            dataframes[csv_file] = frame_csv(file_path)
    return dataframes

def save_dataframes(dataframes_dict, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for filename, df in dataframes_dict.items():
        output_file_path = os.path.join(output_dir, filename)
        df.to_csv(output_file_path, index=False)


# Reconcile specific

def get_bank_files(dir_path):
    """
    Collect all bank files and organize them by bank and year-month.
    Returns a dictionary with banks as keys and sorted lists of year-months as values.
    """
    bank_files = defaultdict(list)
    
    for filename in os.listdir(dir_path):
        if not filename.endswith('.csv'):
            continue            
        # Assuming filename format: bank_YYYY-MM.csv
        bank, year_month = filename.replace('.csv', '').split('_')
        bank_files[bank].append(year_month)
    
    return {bank: sorted(year_months) for bank, year_months in bank_files.items()}


def load_reconciled_data():
    config = load_config()
    reconciled_path = config["paths"]["data_reconciled"]
    banks = config["banks"]

    data = {bank: None for bank in banks}
    files = os.listdir(reconciled_path)
    for bank in banks:
        bank_file = next((f for f in files if f.startswith(bank) and f.endswith(".csv")), None)
        if bank_file:
            file_path = os.path.join(reconciled_path, bank_file)
            try:
                data[bank] = frame_csv(file_path)
                print(f"Successfully loaded data for {bank}: {len(data[bank])} rows")
            except Exception as e:
                print(f"Error loading data for {bank} {str(e)}")
        else:
            print(f"No reconciled file found for {bank}")
    return data


# Dashboard specific

def load_dashboard_data():
    config = load_config()
    reconciled_path = config["paths"]["data_reconciled"]
    banks = config["banks"]
    data = {bank: None for bank in banks}
    files = os.listdir(reconciled_path)
    for bank in banks:
        bank_file = next((f for f in files if f.startswith(bank) and f.endswith(".csv")), None)
        if bank_file:
            file_path = os.path.join(reconciled_path, bank_file)
            try:
                data[bank] = frame_csv(file_path)
                print(f"Successfully loaded data for {bank}: {len(data[bank])} rows")
            except Exception as e:
                print(f"Error loading data for {bank} {str(e)}")
        else:
            print(f"No reconciled file found for {bank}")
    return data

