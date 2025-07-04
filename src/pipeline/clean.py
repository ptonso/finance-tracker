"""
**Automatic cleaner for extracts**

- input:  `data/00--raw`
- output: `data/01--cleaned`

process raw extracts and automatic clean. its currently supporting `nubank` and `inter` extracts.
"""

import os
from src.clean.build_extracts_dict import build_extracts_dict
from src.clean.nubank.clean_extract import process_nubank_df
from src.clean.inter.clean_extract import process_inter_df

def clean_data(config):
    extract_base_dir=config["paths"]["data_raw"]
    cleaned_base_dir=config["paths"]["data_cleaned"]

    all_extract_dict = build_extracts_dict(extract_base_dir)

    nubank = all_extract_dict['nubank']
    inter = all_extract_dict['inter']

    os.makedirs(cleaned_base_dir, exist_ok=True)

    for yearmonth, monthly_df in nubank.items():
        nubank[yearmonth] = process_nubank_df(monthly_df)
        nubank[yearmonth].to_csv(os.path.join(cleaned_base_dir, f"nubank_{yearmonth}.csv"), index=False)

    for yearmonth, monthly_df in inter.items():
        inter[yearmonth] = process_inter_df(monthly_df)
        inter[yearmonth].to_csv(os.path.join(cleaned_base_dir, f"inter_{yearmonth}.csv"), index=False)


if __name__ == "__main__":
    from src.utils.config import load_config
    config = load_config()
    clean_data(config)