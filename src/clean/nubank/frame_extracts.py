"""
Module for framing Nubank extract files and extracting information.
"""
import pandas as pd
from typing import Tuple, List, Optional

PT_MONTHS = {
    "JAN": "01", "FEV": "02", "MAR": "03", "ABR": "04",
    "MAI": "05", "JUN": "06", "JUL": "07", "AGO": "08",
    "SET": "09", "OUT": "10", "NOV": "11", "DEZ": "12"
}

def month2number(date_str: str, months: dict) -> str:
    """Convert month abbreviation to number."""
    for pt_month, month_num in months.items():
        date_str = date_str.replace(pt_month, month_num)
    return date_str

def parse_dates_from_filename(filename: str) -> Tuple[pd.Timestamp, pd.Timestamp]:
    """Extract start and end dates from Nubank filename."""
    date_part = filename.split('_')[-2:]
    start_date = date_part[0][:2] + month2number(date_part[0][2:5], PT_MONTHS) + date_part[0][5:9]
    end_date = date_part[1][:2] + month2number(date_part[1][2:5], PT_MONTHS) + date_part[1][5:9]
    
    start_date = pd.to_datetime(start_date.strip(), format='%d%m%Y')
    end_date = pd.to_datetime(end_date.strip(), format='%d%m%Y')
    
    return start_date, end_date

def read_csv(csv_path: str, year_month: Optional[str] = None) -> pd.DataFrame:
    """
    Read Nubank CSV with appropriate parameters.
    If year_month is provided, filter for that specific month.
    
    Args:
        csv_path: Path to the CSV file
        year_month: Optional string in format 'YYYY-MM' to filter specific month
        
    Returns:
        DataFrame containing only the specified month's data
    """
    df = pd.read_csv(
        csv_path,
        delimiter=',',
        parse_dates=['Data'],
        dayfirst=True,
        decimal='.'
    )
    
    if year_month:
        year, month = map(int, year_month.split('-'))
        df = df[
            (df['Data'].dt.year == year) & 
            (df['Data'].dt.month == month)
        ]
        
    return df

