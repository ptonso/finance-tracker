import os
from glob import glob
import calendar
from copy import deepcopy
import pandas as pd

'''
main function "build_extracts_dict"

this api receive a dir with bank extracts
and return a dicionary of dictionaries of dataframes
bank-name
    month-name ('mm-yyyy')
        dataframe
'''

def is_month_complete(start_date, end_date):
    days_in_month = calendar.monthrange(start_date.year, start_date.month)[1]
    return (start_date.day == 1) and (end_date.day == days_in_month)

pt_months = {
        "JAN": "01", "FEV": "02", "MAR": "03", "ABR": "04",
        "MAI": "05", "JUN": "06", "JUL": "07", "AGO": "08",
        "SET": "09", "OUT": "10", "NOV": "11", "DEZ": "12"
    }


def month2number(date_str, months):
    
    for pt_month, month_num in months.items():
        date_str = date_str.replace(pt_month, month_num)
    return date_str

def parse_dates_from_nubank_filename(filename):
    date_part = filename.split('_')[-2:]
    start_date = date_part[0][:2] + month2number(date_part[0][2:5], pt_months) + date_part[0][5:9]
    end_date = date_part[1][:2] + month2number(date_part[1][2:5], pt_months) + date_part[1][5:9]
    
    start_date = pd.to_datetime(start_date.strip(), format='%d%m%Y')
    end_date = pd.to_datetime(end_date.strip(), format='%d%m%Y')
    
    return start_date, end_date

def read_csv_nubank(csv_path):
    df = pd.read_csv(
        csv_path,
        delimiter=',',
        parse_dates=['Data'],
        dayfirst=True,
        decimal='.'
    )
    return df

def parse_dates_from_inter_filename(filename):
    date_part = filename.split('-')[1:]
    start_date = ''.join(date_part[0:3])
    end_date = ''.join(date_part[4:6] + [date_part[6].split('.')[0]])

    start_date = pd.to_datetime(start_date.strip(), format='%d%m%Y')
    end_date = pd.to_datetime(end_date.strip(), format='%d%m%Y')
    
    return start_date, end_date

def read_csv_inter(csv_path):
    df = pd.read_csv(
        csv_path,
        delimiter=';',
        skiprows=3,
        parse_dates=['Data Lançamento'],
        dayfirst=True,
        decimal=','
    )
    return df

def build_extracts_dict(extract_base_dir="data/00_raw"):

    all_extract_dict = {'nubank': {},
                        'inter': {}}

    longest_range_files = deepcopy(all_extract_dict)
    extract_csv_paths = glob(os.path.join(extract_base_dir, '*'))

    for csv_path in extract_csv_paths:
        filename = os.path.basename(csv_path)

        bank = None

        if 'NU' in filename:
            bank = 'nubank'
            start_date, end_date = parse_dates_from_nubank_filename(filename)
        elif 'Extrato' in filename:
            bank = 'inter'
            start_date, end_date = parse_dates_from_inter_filename(filename)
        else:
            continue

        year_month = f"{start_date.year}-{start_date.month:02d}"

        if year_month not in longest_range_files[bank]:
            longest_range_files[bank][year_month] = (csv_path, start_date, end_date)
        else:
            _, existing_start_date, existing_end_date = longest_range_files[bank][year_month]
            existing_range = (existing_end_date - existing_start_date).days
            current_range = (end_date - start_date).days
            if current_range > existing_range:
                longest_range_files[year_month] = (csv_path, start_date, end_date)


    for bank in longest_range_files:
        for year_month, (csv_path, start_date, end_date) in longest_range_files[bank].items():
            
            if bank == 'nubank':
                df = read_csv_nubank(csv_path)
            elif bank == 'inter':
                df = read_csv_inter(csv_path)

            all_extract_dict[bank][year_month] = df

            if not is_month_complete(start_date, end_date):
                print(f"Incomplete month: {year_month} in {bank}")


    for bank, months in all_extract_dict.items():
        print(f"\nBank: {bank.capitalize()}")
        years = {}
        for year_month in months:
            year = year_month.split('-')[0]
            if year not in years:
                years[year] = []
            years[year].append(year_month.split('-')[1])

        for year in sorted(years.keys()):
            print(f"  Year: {year}")
            for month in sorted(years[year]):
                month_name = [name for name, v in pt_months.items() if v == month][0]
                print(f"    {month}-{month_name}")

    return all_extract_dict


def frame_csv(csv_path):
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'])
    df['income'] = df['income'].astype(float)
    df['outcome'] = df['outcome'].astype(float)
    df['bank'] = df['bank'].astype(str)
    df['category'] = df['category'].astype(str)
    df['description'] = df['description'].astype(str)
    df['original_id'] = df['original_id'].astype(str)
    return df


def frame_dir(dir_path="data/02_reconciled"):
    full_df = pd.DataFrame()
    for file_name in os.listdir(dir_path):
        if file_name.endswith(".csv"):
            file_path = os.path.join(dir_path, file_name)
            df = frame_csv(file_path)
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            full_df = pd.concat([full_df, df], ignore_index=True)
    return full_df


def save_reconciled_data(full_df, reconciled_path="data/02_reconciled"):
    os.makedirs(reconciled_path, exist_ok=True)

    if not pd.api.types.is_datetime64_any_dtype(full_df['date']):
        full_df['date'] = pd.to_datetime(full_df['date'])
    
    full_df['year_month'] - full_df['date'].dt.strftime('%Y-%m')
    grouped = full_df.groupby(['bank', 'year_month'])

    for (bank, year_month), group in grouped:
        file_name = f"{bank}+{year_month}.csv"
        file_path = os.path.join(reconciled_path, file_name)

        group.drop(columns=["year_month"], inpalce=True)
        group.to_csv(file_path, index=False)
        print(f"Saved {file_path}")

    print("All files saves successfully.")

    