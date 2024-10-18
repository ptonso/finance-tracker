

import numpy as np
import pandas as pd
import random
from datetime import datetime, timedelta

categories = {
    'fixed_high': ['housing', 'taxes'],
    'variable_fixed': ['supplies', 'utilities'],
    'variable_low': ['eating-out', 'transport', 'snack', 'fun-money', 'healthcare', 'clothing', 'personal-enrichment'],
    'income': ['account-transfer', 'monthly-income', 'allowance', 'sales', 'investment-return', 'savings'],
    'other': ['other', 'home-maintenance', 'e-commerce', 'subscription']
}

def random_date(start, end):
    """Generate a random date between two dates."""
    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + timedelta(days=random_days)

def random_string():
    """Generate a random string for original_id."""
    return ''.join(random.choices('abcdef' + '0123456789', k=36))

def generate_transactions(start_date, months=20, transactions_per_month=70):
    dates = []
    banks = []
    incomes = []
    outcomes = []
    balances = []
    categories_list = []
    descriptions = []
    original_ids = []
    
    balance = 0.0
    current_date = start_date
    
    for month in range(months):
        for _ in range(transactions_per_month):
            bank = random.choice(['nubank'])
            
            category_type = random.choices(['fixed_high', 'variable_fixed', 'variable_low', 'income', 'other'], [0.1, 0.2, 0.5, 0.15, 0.05])[0]
            category = random.choice(categories[category_type])
            
            if category_type == 'income':
                income = round(random.uniform(1000, 5000), 2)
                outcome = 0.0
            else:
                income = 0.0
                if category_type == 'fixed_high':
                    outcome = round(random.uniform(1000, 3000), 2)
                elif category_type == 'variable_fixed':
                    outcome = round(random.uniform(200, 1000), 2)
                else:  # variable_low and other
                    outcome = round(random.uniform(10, 500), 2)
            
            balance += (income - outcome)
            
            month_start = current_date.replace(day=1)
            next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
            transaction_date = random_date(month_start, next_month - timedelta(days=1))
            
            dates.append(transaction_date.strftime('%Y-%m-%d'))
            banks.append(bank)
            incomes.append(income)
            outcomes.append(outcome)
            balances.append(balance)
            categories_list.append(category)
            descriptions.append(f"Sample description for {category}")
            original_ids.append(random_string())
        
        current_date = next_month
    
    df = pd.DataFrame({
        'date': dates,
        'bank': banks,
        'income': incomes,
        'outcome': outcomes,
        'balance': balances,
        'category': categories_list,
        'description': descriptions,
        'original_id': original_ids
    })
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    
    return df

start_date = datetime(2023, 1, 1)
df = generate_transactions(start_date)

