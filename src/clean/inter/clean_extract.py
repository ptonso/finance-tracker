import pandas as pd
from typing import List
from src.utils.config import load_config

config = load_config()
STANDARD_COLUMNS = config['data_processing']['standard_columns']
BANK_NAME = 'inter'

def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize column names to match system requirements."""
    df['full_description'] = df['Histórico'] + ' ' + df["Descrição"]
    column_mapping = {
        'Data Lançamento': 'date',
        'Valor': 'value',
        'full_description': 'description',
        'Descrição': 'participant'
    }
    df = df.rename(columns=column_mapping)
    return df

def convert_date_format(df: pd.DataFrame) -> pd.DataFrame:
    """Convert date string to datetime format."""
    df['date'] = pd.to_datetime(df['date'])
    return df

def convert_value_to_float(df: pd.DataFrame) -> pd.DataFrame:
    """Convert value column to float type."""
    # Remove thousand separators and replace decimal comma with point
    df['value'] = df['value'].str.replace('.', '').str.replace(',', '.').astype(float)
    return df

def split_transaction_values(df: pd.DataFrame) -> pd.DataFrame:
    """Split value into separate income and outcome columns."""
    df['income'] = df['value'].apply(lambda x: x if x > 0 else 0)
    df['outcome'] = df['value'].apply(lambda x: -x if x < 0 else 0)
    df.drop(columns=['value'], inplace=True)
    return df

def clean_text_fields(df: pd.DataFrame) -> pd.DataFrame:
    """Clean description and participant fields."""
    def clean_text(desc: str) -> str:
        return ' '.join(str(desc).split()).strip()
    df['description'] = df['description'].apply(clean_text)
    df['participant'] = df['participant'].apply(clean_text)
    return df

def standardize_text_fields(df: pd.DataFrame, exclude_columns: List[str]) -> pd.DataFrame:
    """Convert text fields to lowercase except for specified columns."""
    string_columns = df.select_dtypes(include='object').columns
    columns_to_process = [col for col in string_columns if col not in exclude_columns]
    df[columns_to_process] = df[columns_to_process].apply(lambda x: x.str.lower())
    return df

def add_standard_fields(df: pd.DataFrame) -> pd.DataFrame:
    """Add standard fields with default values."""
    df['bank'] = BANK_NAME
    df['balance'] = 0.0  # We could potentially use 'Saldo' column if needed
    df['category'] = ''
    return df

def reorder_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Reorder columns to match standard format."""
    return df.reindex(columns=STANDARD_COLUMNS)

def process_inter_df(monthly_df: pd.DataFrame) -> pd.DataFrame:
    """
    Process Inter bank transaction data.
    
    Args:
        monthly_df: Raw DataFrame from Inter bank export
        
    Returns:
        Processed DataFrame with standardized columns and formats
    """
    processed_df = (
        monthly_df
        .pipe(standardize_column_names)
        .pipe(convert_date_format)
        .pipe(convert_value_to_float)
        .pipe(split_transaction_values)
        .pipe(clean_text_fields)
        .pipe(standardize_text_fields, exclude_columns=['original_id'])
        .pipe(add_standard_fields)
        .pipe(reorder_columns)
    )
    return processed_df