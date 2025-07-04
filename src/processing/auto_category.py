import os

from src.utils.load_data import load_json, frame_csv
from src.utils.config import load_config
config = load_config()

DEFAULT_CATEGORY = config["data_processing"]["default_category"]
CATEGORY_LOOKUP = config["lookup"]["category"]


def load_categories():
    return list(load_json(CATEGORY_LOOKUP).keys())

def load_category_lookup():
    return load_json(CATEGORY_LOOKUP)

def desc2category(description, lookup_table):
    for cat, keywords in lookup_table.items():
        filtered_keywords = [kw for kw in keywords if kw]
        if not filtered_keywords:
            continue
        if any(keyword.lower() in description.lower() for keyword in filtered_keywords):
            return cat
    return DEFAULT_CATEGORY

def desc2type(description, lookup_table):
    for type, keywords in lookup_table.items():
        filtered_keywords = [kw for kw in keywords if kw]
        if not filtered_keywords:
            continue
        if any(keyword.lower() in type.lower() for keyword in filtered_keywords):
            return type
    return DEFAULT_CATEGORY

def categorize_dataframes(dataframes_dict, lookup_table, show_stats=True):
    categorized_dfs = {}
    stats = {}
    
    for filename, df in dataframes_dict.items():
        categorized_df = df.copy()
        categorized_df['category'] = categorized_df['description'].apply(
            lambda x: desc2category(x, lookup_table)
        )
        
        default_count = (categorized_df['category'] == DEFAULT_CATEGORY).sum()
        total_count = categorized_df.shape[0]
        
        categorized_dfs[filename] = categorized_df
        stats[filename] = {
            'default_count': default_count,
            'total_count': total_count
        }
    
    if show_stats:
        print("="*50)
        print(f"csv file            : proportion of rows categorized as '{DEFAULT_CATEGORY}'")
        print("="*50)
        for filename, stat in stats.items():
            print(f"{filename:<20}: {stat['default_count']:<3} of {stat['total_count']:<3}")

    return categorized_dfs


def categorize_from_lookup(input_dir, output_dir, lookup_table):
    os.makedirs(output_dir, exist_ok=True)

    print("="*50)
    print(f"csv file            : proportion of rows categorized as '{DEFAULT_CATEGORY}")
    print("="*50)
    for csv_file in os.listdir(input_dir):
        if csv_file.endswith(".csv"):
            file_path = os.path.join(input_dir, csv_file)
            df = frame_csv(file_path)

            df['category'] = df['description'].apply(lambda x: desc2category(x, lookup_table))
            default_count = (df['category'] == DEFAULT_CATEGORY).sum()
            total_count = df.shape[0]

            output_file_path = os.path.join(output_dir, csv_file)
            df.to_csv(output_file_path, index=False)
            print(f"{csv_file:<20}: {default_count:<3} of {total_count:<3}")


