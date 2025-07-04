import os
import json
import pandas as pd
from src.utils.load_data import frame_csv
from src.utils.load_data import get_bank_files

from src.utils.config import load_config
config = load_config()
BALANCE_PATH = config['lookup']['balances']


def load_balance_dict():    
    with open(BALANCE_PATH, 'r') as f:
        return json.load(f)


def create_adjustment_entry(date, bank, current_balance, target_balance=None, is_initial=False):
    """
    Create an adjustment entry (either initial balance or reconciliation).
    """
    if is_initial:
        # For initial balance, we directly set the amount as income/outcome
        amount = target_balance or 0.0
        category = 'initial balance'
        description = ''
    else:
        # For reconciliation, we calculate the adjustment needed
        if target_balance is None:
            amount = 0.0
            category = 'reconciler-adjustment'
            description = 'no balance data available'
            target_balance = current_balance  # Keep the same balance
        else:
            amount = target_balance - current_balance
            category = 'reconciler-adjustment'
            description = ''

    return pd.DataFrame({
        'date': [date],
        'bank': [bank],
        'income': [amount if amount > 0 else 0],
        'outcome': [-amount if amount < 0 else 0],
        'category': [category],
        'description': [description],
        'original_id': [''],
        'balance': [target_balance]
    })

def process_monthly_extract(df, initial_balance=0.0):
    """Calculate running balances for a monthly extract."""
    df['balance'] = initial_balance + (df['income'].fillna(0) - df['outcome'].fillna(0)).cumsum()
    return df


def get_date_range_str(dates):
    sorted_dates = sorted(dates)
    return f"{sorted_dates[0]}_{sorted_dates[-1]}"


def reconcile_extracts(balances, input_dir, output_dir):
    """
    Main reconciliation function.
    Processes each bank's extracts chronologically, adding initial balance
    and reconciliation entries as needed.
    """
    os.makedirs(output_dir, exist_ok=True)
    bank_files = get_bank_files(input_dir)
    
    for bank in bank_files:
        print(f"\nProcessing bank: {bank}")
        bank_balances = balances.get(bank, {})
        
        # Get initial balance (0.0 if not specified)
        initial_balance = bank_balances.get('initial', 0.0)
        previous_balance = initial_balance

        monthly_dfs = []
        
        for i, year_month in enumerate(bank_files[bank]):
            input_path = os.path.join(input_dir, f"{bank}_{year_month}.csv")
            output_path = os.path.join(output_dir, f"{bank}_{year_month}.csv")
            
            print(f"Processing {year_month}")
            df = frame_csv(input_path)
            
            # For first month, add initial balance entry
            if i == 0:
                initial_entry = create_adjustment_entry(
                    date=df.iloc[0]['date'],
                    bank=bank,
                    current_balance=0.0,  # Starting from zero
                    target_balance=initial_balance,
                    is_initial=True
                )
                df = pd.concat([initial_entry, df], ignore_index=True)
            
            # Calculate running balances
            df = process_monthly_extract(df, previous_balance)
            current_balance = df['balance'].iloc[-1]
            
            # Add reconciliation entry (always)
            target_balance = bank_balances.get(year_month)
            reconciliation = create_adjustment_entry(
                date=df.iloc[-1]['date'],
                bank=bank,
                current_balance=current_balance,
                target_balance=target_balance,
                is_initial=False
            )
            
            # Add reconciliation entry and update balances
            df = pd.concat([df, reconciliation], ignore_index=True)
                       
            if target_balance is not None:
                previous_balance = target_balance
                print(f"Reconciled to target balance: {target_balance:.2f}")
            else:
                previous_balance = current_balance
                print(f"No target balance available. Maintained at: {current_balance:.2f}")

            monthly_dfs.append(df)

        bank_df = pd.concat(monthly_dfs, ignore_index=True)

        date_range = get_date_range_str(bank_files[bank])
        output_path = os.path.join(output_dir, f"{bank}_{date_range}.csv")

        bank_df.to_csv(output_path, index=False)
        print(f"Saved consolidated file: {output_path}")


# ---------

def main(input_dir, output_dir):
    """Main entry point for the reconciliation process."""
    try:
        balances = load_balance_dict()
        reconcile_extracts(balances, input_dir, output_dir)
        print("\nReconciliation completed successfully!")
    except Exception as e:
        print(f"\nError during reconciliation: {str(e)}")
        raise

if __name__ == "__main__":
    from src.utils.config import load_config
    config = load_config()
    main(
        input_dir="path/to/input",
        output_dir="path/to/output",
    )
    