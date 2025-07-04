"""
Module for framing Inter extract files and extracting information.
"""
import pandas as pd
from typing import Tuple, List, Optional

def parse_dates_from_filename(filename: str) -> Tuple[pd.Timestamp, pd.Timestamp]:
    """Extract start and end dates from Inter filename."""
    date_part = filename.split('-')[1:]
    start_date = ''.join(date_part[0:3])
    end_date = ''.join(date_part[4:6] + [date_part[6].split('.')[0]])

    start_date = pd.to_datetime(start_date.strip(), format='%d%m%Y')
    end_date = pd.to_datetime(end_date.strip(), format='%d%m%Y')
    
    return start_date, end_date

def read_csv(csv_path: str, year_month: Optional[str] = None) -> pd.DataFrame:
    """
    Read Inter CSV with appropriate parameters.
    If year_month is provided, filter for that specific month.
    
    Args:
        csv_path: Path to the CSV file
        year_month: Optional string in format 'YYYY-MM' to filter specific month
        
    Returns:
        DataFrame containing only the specified month's data
    """
    df = pd.read_csv(
        csv_path,
        delimiter=';',
        skiprows=3,
        parse_dates=['Data Lançamento'],
        dayfirst=True,
        decimal=','
    )
    
    if year_month:
        year, month = map(int, year_month.split('-'))
        df = df[
            (df['Data Lançamento'].dt.year == year) & 
            (df['Data Lançamento'].dt.month == month)
        ]
        
    return df

