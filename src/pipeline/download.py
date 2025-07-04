"""
**Data downloander**

- input:  external
- output: `data/00--raw`

For NuBank data, go to the mobile App, Extrato and then select the months to download.
They will send you an email with the csv.

With `.env` setup, this script will download data from your Extracts GoogleDrive folder to raw

If you want just to get started, manually download the csv inside `data/00--raw`, and you are good to go.
"""

import os
from src.download.sheets_api import download_extracts

def donwload_data(config):
    
    drive_folder_id = os.getenv("DRIVE_EXTRACTS_ID")
    local_folder_path = config["paths"]["data_raw"]

    if drive_folder_id is None:
        print("before downloading the data, configure variable DRIVE_EXTRACTS_ID inside `.env` with the ID of GoogleDrive extracts folder.")

    download_extracts(drive_folder_id, local_folder_path, debug=False)


if __name__ == "__main__":
    from src.utils.config import load_config
    config = load_config()

    donwload_data(config)