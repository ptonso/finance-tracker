
import pandas as pd

def relabel_columns(df, columns):
    df.columns = columns
    return df

def convert_to_datetime(df, column):
    df[column] = pd.to_datetime(df[column], dayfirst=True)
    return df

def convert_to_float(df, column):
    df[column] = df[column].astype(float)
    return df

def split_inout_value(df, column):
    df['income'] = df[column].apply(lambda x: x if x > 0 else 0)
    df['outcome'] = df[column].apply(lambda x: -x if x < 0 else 0)
    df.drop(columns=[column], inplace=True)
    return df


def remove_comma(df, column):
    df[column] = df[column].apply(lambda x: x.replace(",", ""))
    return df


def lowercase_string_columns(df, exclude_columns):
    string_columns = df.select_dtypes(include='object').columns
    columns_to_process = [col for col in string_columns if col not in exclude_columns]
    df[columns_to_process] = df[columns_to_process].apply(lambda x: x.str.lower())
    return df


def process_nubank_df(monthly_df):
    columns = ["date", "value", "original_id", "description"]
    
    monthly_df = relabel_columns(monthly_df, columns)
    monthly_df = convert_to_datetime(monthly_df, 'date')
    monthly_df = convert_to_float(monthly_df, 'value')
    monthly_df = split_inout_value(monthly_df, 'value')
    monthly_df = remove_comma(monthly_df, 'description')
    
    monthly_df = lowercase_string_columns(monthly_df, ['original_id'])

    monthly_df['bank'] = 'nubank'
    monthly_df['balance'] = 0.
    monthly_df['category'] = ''

    col_order = ['date', 'bank', 'income', 'outcome', 'balance', 'category', 'description', 'original_id']
    monthly_df = monthly_df.reindex(columns=col_order)

    return monthly_df
