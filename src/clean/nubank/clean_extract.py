import pandas as pd
from typing import List
from src.utils.config import load_config


config = load_config()
STANDARD_COLUMNS = config['data_processing']['standard_columns']
BANK_NAME = 'nubank'


def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize column names to match system requirements."""
    standard_names = ["date", "value", "original_id", "description"]
    df.columns = standard_names
    return df


def convert_date_format(df: pd.DataFrame) -> pd.DataFrame:
    """Convert date string to datetime format."""
    df['date'] = pd.to_datetime(df['date'], dayfirst=True)
    return df


def convert_value_to_float(df: pd.DataFrame) -> pd.DataFrame:
    """Convert value column to float type."""
    df['value'] = df['value'].astype(float)
    return df


def split_transaction_values(df: pd.DataFrame) -> pd.DataFrame:
    """Split value into separate income and outcome columns."""
    df['income'] = df['value'].apply(lambda x: x if x > 0 else 0)
    df['outcome'] = df['value'].apply(lambda x: -x if x < 0 else 0)
    df.drop(columns=['value'], inplace=True)
    return df


def clean_description(df: pd.DataFrame) -> pd.DataFrame:
    """Remove commas from description field."""
    def clean_description(desc: str) -> str:
        desc.replace(",", "")
        return ' '.join(desc.split()).strip()
    df['description'] = df['description'].apply(clean_description)
    return df


def extract_participant(df: pd.DataFrame) -> pd.DataFrame:
    """Extract participant information from description field."""
    def get_participant(desc: str) -> str:
        parts = desc.split(" - ")
        return parts[1].lower() if len(parts) > 1 else ""
        
    df['participant'] = df['description'].apply(get_participant)
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
    df['balance'] = 0.0
    df['category'] = ''
    return df


def reorder_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Reorder columns to match standard format."""
    return df.reindex(columns=STANDARD_COLUMNS)


def process_nubank_df(monthly_df: pd.DataFrame) -> pd.DataFrame:
    """
    Process Nubank transaction data.
    
    Args:
        monthly_df: Raw DataFrame from Nubank export
        
    Returns:
        Processed DataFrame with standardized columns and formats
    """
    processed_df = (
        monthly_df
        .pipe(standardize_column_names)
        .pipe(convert_date_format)
        .pipe(convert_value_to_float)
        .pipe(split_transaction_values)
        .pipe(clean_description)
        .pipe(extract_participant)
        .pipe(standardize_text_fields, exclude_columns=['original_id'])
        .pipe(add_standard_fields)
        .pipe(reorder_columns)
    )
    
    return processed_df
