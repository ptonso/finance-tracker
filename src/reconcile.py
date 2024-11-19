import os
import json
import pandas as pd

from .frame_csv import frame_csv
from dotenv import load_dotenv
load_dotenv()

def load_balances():
    balances_path = os.getenv("BALANCES_PATH")
    with open(balances_path, 'r') as f:
        balances = json.load(f)
    return balances



def reconcile_balances(balances, input_dir, output_dir):
    for bank, bank_data in balances.items():
        print(f"Processing bank: {bank}")
        months = sorted([key for key in bank_data.keys() if key != "initial"])
        previous_balance = bank_data['initial']

        for month in months:
            file_path = os.path.join(input_dir, f"{bank}_{month}.csv")
            output_path = os.path.join(output_dir, f"{bank}_{month}.csv")
            if not os.path.exists(file_path):
                print(f"File not found for {bank} in {month}: {file_path}")
                continue

            df = frame_csv(file_path)
            df['balance'] = previous_balance + (df['income'].fillna(0) - df['outcome'].fillna(0)).cumsum()

            final_balance = df['balance'].iloc[-1]

            target_balance = bank_data.get(month, None)
            if target_balance is None:
                print(f"Target balance for {bank} in {month} is None. Adding 0.0 reconciliation adjustment")
                target_balance = final_balance

            adjustment_amount = target_balance - final_balance

            reconciler_transaction = pd.DataFrame({
                'date': [df.iloc[-1]['date']],
                'bank': [bank],
                'income': [adjustment_amount if adjustment_amount > 0 else 0],
                'outcome': [-adjustment_amount if adjustment_amount < 0 else 0],
                'category': ['reconciler adjustment'],
                'description': [''],
                'original_id': [''],
                'balance': [target_balance],
            })

            df = pd.concat([df, reconciler_transaction], ignore_index=True)
            df['balance'] = previous_balance + (df['income'].fillna(0) - df['outcome'].fillna(0)).cumsum()

            df.to_csv(output_path, index=False)

            print(f"Bank: {bank}, Month: {month}, Final Balance: {df['balance'].iloc[-1]:.2f}, Adjustment: {adjustment_amount:.2f}")
            previous_balance = target_balance

