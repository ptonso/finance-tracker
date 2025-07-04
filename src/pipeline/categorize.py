"""
**Categorization**

- input:  `data/01_cleaned`
- output: `data/02_categorized`

## Lookup categorization
the process will use `category_lookup.json` to automatic categorize based on word match in `description`.
update the `category_lookup.json` manually (but only once).

## Machine learning
after gathering sufficient categorized data, we can use machine learning to automate categorization process.
"""

import os
from src.processing.auto_category import load_category_lookup, categorize_dataframes
# from src.processing.auto_type import load_type_rules, typefy_dataframes
from src.utils.load_data import load_dataframes_from_dir, save_dataframes

def categorize_data(config):
    category_lookup = load_category_lookup()
    # type_lookup = load_type_lookup()

    input_dir = config["paths"]["data_cleaned"]
    output_dir = config["paths"]["data_categorized"]

    os.makedirs(output_dir, exist_ok=True)

    dfs = load_dataframes_from_dir(input_dir)

    # typed_dfs = typefy_dataframes(dfs, type_lookup)
    categorized_dfs = categorize_dataframes(dfs, category_lookup)

    save_dataframes(categorized_dfs, output_dir)

    print(dfs)


if __name__ == "__main__":
    from src.utils.config import load_config
    config = load_config()
    categorize_data(config)