
from typing import Dict
from src.utils.load_data import load_json
from src.utils.config import load_config
config = load_config()


TYPE_LOOKUP = config["lookup"]["type"]


def load_types():
    return list(load_json(TYPE_LOOKUP).keys())

def load_type_rules():
    return load_json(TYPE_LOOKUP)


def initialize_rules():
    type_rules = load_type_rules()

    processed_rules = []
    for type_name, type_rules in type_rules.items():
        processed_rules[type_name] = []
        for rule in type_rules['rules']:
            try:
                processed_rules = rule.copy()
                processed_rules['condition'] = eval(rule['condition'])
                processed_rules[type_name].append(processed_rules)
            except Exception as e:
                print(f"Error processing rule {rule['name']} for type {type_name}: {e}")
    return processed_rules

def determine_type(rules, transaction: Dict[str, Any]) -> str:
    for type_name, type_rules in rules.items():
        for rule in type_rules:
            try:
                if rule['condition'](transaction):
                    return type_name
            except Exception as e:
                print(f"Error evaluating rule {rule['name']}: {e}")
                continue
    return config["data_processing"]["default_type"]


def typefy_dataframes(dataframes_dict: Dict[str, 'pd.DataFrame']) -> Dict[str, 'pd.DataFrame']:

    typed_dfs = {}
    for filename, df in dataframes_dict.items():
        typed_df = df.copy()

        typed_df['type'] = typed_df.apply(
            lambda row: determine_type(row.to_dict()),
            axis=1
        )

        typed_dfs[filename] = typed_df

    return typed_dfs

