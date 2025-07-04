"""
Module for building dictionary of bank extracts.
Coordinates the framing of different bank extracts.
"""
import os
from glob import glob
import calendar
from copy import deepcopy
import pandas as pd
from typing import Dict, Tuple, List

from src.clean.nubank.frame_extracts import (
    parse_dates_from_filename as parse_nubank_dates,
    read_csv as read_nubank_csv
)
from src.clean.inter.frame_extracts import (
    parse_dates_from_filename as parse_inter_dates,
    read_csv as read_inter_csv
)

def get_months_in_range(start_date: pd.Timestamp, end_date: pd.Timestamp) -> List[str]:
    """
    Get list of year-month strings between start and end dates.
    
    Args:
        start_date: Start date of the range
        end_date: End date of the range
        
    Returns:
        List of strings in format ['YYYY-MM', ...]
    """
    months = pd.date_range(
        start=start_date,
        end=end_date,
        freq='MS'  # Month Start frequency
    )
    return [f"{date.year}-{date.month:02d}" for date in months]

def is_month_complete(start_date: pd.Timestamp, end_date: pd.Timestamp, year_month: str) -> bool:
    """
    Check if extract covers complete month.
    
    Args:
        start_date: Start date of extract
        end_date: End date of extract
        year_month: Year-month string to check (YYYY-MM)
        
    Returns:
        True if the month is completely covered
    """
    year, month = map(int, year_month.split('-'))
    days_in_month = calendar.monthrange(year, month)[1]
    
    month_start = pd.Timestamp(year=year, month=month, day=1)
    month_end = pd.Timestamp(year=year, month=month, day=days_in_month)
    
    return start_date <= month_start and end_date >= month_end

def build_extracts_dict(extract_base_dir: str = "data/00_raw") -> Dict[str, Dict[str, pd.DataFrame]]:
    """
    Build dictionary of bank extracts, handling multi-month extracts.
    
    Args:
        extract_base_dir: Directory containing bank extract files
        
    Returns:
        Dict with structure: {'bank_name': {'YYYY-MM': DataFrame}}
    """
    all_extract_dict = {'nubank': {}, 'inter': {}}
    extract_coverage = {'nubank': {}, 'inter': {}}
    
    pattern = os.path.join(extract_base_dir, '**', '*.csv')
    extract_csv_paths = glob(pattern, recursive=True)

    # First pass: Find all available months from all extracts
    for csv_path in extract_csv_paths:
        filename = os.path.basename(csv_path)

        try:
            if 'NU' in filename:
                bank = 'nubank'
                start_date, end_date = parse_nubank_dates(filename)
                months = get_months_in_range(start_date, end_date)
            elif 'Extrato' in filename:
                bank = 'inter'
                start_date, end_date = parse_inter_dates(filename)
                months = get_months_in_range(start_date, end_date)
            else:
                continue

            # Record coverage for each month
            for month in months:
                if month not in extract_coverage[bank]:
                    extract_coverage[bank][month] = []
                
                coverage_info = {
                    'path': csv_path,
                    'start_date': start_date,
                    'end_date': end_date,
                    'is_complete': is_month_complete(start_date, end_date, month)
                }
                extract_coverage[bank][month].append(coverage_info)

        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            continue

    # Second pass: Choose best extract for each month and read data
    for bank in extract_coverage:
        for month in extract_coverage[bank]:
            try:
                # Prefer complete month extracts
                month_files = extract_coverage[bank][month]
                complete_files = [f for f in month_files if f['is_complete']]
                
                if complete_files:
                    chosen_file = max(complete_files, 
                        key=lambda x: (x['end_date'] - x['start_date']).days)
                else:
                    chosen_file = max(month_files, 
                        key=lambda x: (x['end_date'] - x['start_date']).days)
                
                # Read only the specific month from the chosen file
                if bank == 'nubank':
                    df = read_nubank_csv(chosen_file['path'], month)
                else:
                    df = read_inter_csv(chosen_file['path'], month)
                
                if not df.empty:
                    all_extract_dict[bank][month] = df
                    
                    if not chosen_file['is_complete']:
                        print(f"Warning: Incomplete month {month} in {bank}")

            except Exception as e:
                print(f"Error reading {month} from {bank}: {str(e)}")
                continue

    # Print summary of available data
    _print_extracts_summary(all_extract_dict)
    
    return all_extract_dict

def _print_extracts_summary(all_extract_dict: Dict[str, Dict[str, pd.DataFrame]]) -> None:
    """Print summary of available extracts by bank and year-month."""
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
                print(f"    {month}")