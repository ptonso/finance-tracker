"""
**Manual curate**

input:  `data/02--categorized`
output: `data/03--reconciled`

reconcile mean to make sure that the balance is correct with real bank account.

The lookup `my_balances.json` is used to input the balance data from the real bank.
Every end of month, you can check your bank acount and add the value to the dictionary. 
The function will add reconciliation points to make sure that your extracts match your real bank balance.
"""


import os
from src.processing.reconcile import reconcile_extracts, load_balance_dict


def reconcile_data(config):
    balances = load_balance_dict()

    input_dir = config["paths"]["data_categorized"]
    output_dir = config["paths"]["data_reconciled"]

    os.makedirs(output_dir, exist_ok=True)

    reconcile_extracts(balances, input_dir, output_dir)


if __name__ == "__main__":
    from src.utils.config import load_config
    config = load_config()
    reconcile_data(config)